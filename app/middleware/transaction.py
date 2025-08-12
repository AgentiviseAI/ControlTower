"""
Database Transaction Middleware
Provides atomic database operations for API endpoints

IMPORTANT: For true atomicity, services must be called with auto_commit=False
to prevent individual operations from committing immediately.

Usage Examples:

1. Using TransactionManager (recommended for complex operations):
   
   @router.post("/complex-operation")
   async def complex_operation(
       transaction_manager: TransactionManager = Depends(get_transaction_manager)
   ):
       def step1():
           return service.create_resource(auto_commit=False)  # ← Key: auto_commit=False
       
       def step2(result1):
           return service.update_related(result1['id'], auto_commit=False)  # ← Key: auto_commit=False
       
       def atomic_operation():
           result1 = step1()
           result2 = step2(result1) 
           return result2
       
       return transaction_manager.execute_atomic([atomic_operation])

2. Testing Atomicity:
   To verify transactions work, cause an intentional error in step 3 and verify
   that steps 1 and 2 are rolled back completely.
"""
from functools import wraps
from contextlib import contextmanager
from typing import Callable, Any, Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
import threading

from app.core.database import get_db
from app.core.exceptions import ConflictError
import logging

logger = logging.getLogger(__name__)

# Thread-local storage to track transaction state
_transaction_context = threading.local()


def is_in_transaction() -> bool:
    """Check if current thread is running within a transaction context"""
    return getattr(_transaction_context, 'active', False)


def set_transaction_context(active: bool):
    """Set the transaction context for current thread"""
    _transaction_context.active = active


@contextmanager
def db_transaction(db: Session) -> Generator[Session, None, None]:
    """
    Context manager for database transactions.
    Ensures all operations within the context are atomic (all or nothing).
    """
    try:
        # Set transaction context
        set_transaction_context(True)
        logger.debug("Starting database transaction")
        yield db
        # Commit on success
        db.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        # Rollback on any error
        logger.error(f"Database transaction failed, rolling back: {str(e)}")
        db.rollback()
        raise
    finally:
        # Clear transaction context
        set_transaction_context(False)
        # Ensure session is closed
        db.close()


class TransactionManager:
    """
    Transaction manager for handling atomic operations in API endpoints
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_atomic(self, operations: list[Callable]) -> Any:
        """
        Execute a list of operations atomically.
        If any operation fails, all changes are rolled back.
        
        Args:
            operations: List of callable functions to execute
            
        Returns:
            Result of the last operation
            
        Raises:
            HTTPException: If any operation fails
        """
        try:
            with db_transaction(self.db):
                result = None
                for operation in operations:
                    result = operation()
                return result
        except ConflictError as e:
            # Re-raise business logic conflicts
            logger.warning(f"Conflict during atomic operation: {str(e)}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except IntegrityError as e:
            # Handle database constraint violations
            logger.error(f"Database integrity error during atomic operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Operation violates database constraints"
            )
        except DataError as e:
            # Handle invalid data errors
            logger.error(f"Data validation error during atomic operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error during atomic operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed"
            )
        except HTTPException:
            # Re-raise HTTP exceptions as-is (like ConflictError converted to HTTPException)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during atomic operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


def get_transaction_manager(db: Session = Depends(get_db)) -> TransactionManager:
    """
    Dependency to get a transaction manager instance
    """
    return TransactionManager(db)


def atomic_operation(func: Callable) -> Callable:
    """
    Decorator to make an entire API endpoint atomic.
    All database operations within the endpoint will be part of a single transaction.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the db session in kwargs
        db = None
        for key, value in kwargs.items():
            if isinstance(value, Session):
                db = value
                break
        
        if not db:
            # If no Session found, try to get it from dependencies
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No database session found for atomic operation"
            )
        
        try:
            with db_transaction(db):
                return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in atomic operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed"
            )
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error in atomic operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    return wrapper
