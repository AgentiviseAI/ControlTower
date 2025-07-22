"""
Repository interfaces and base implementations following SOLID principles
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Session

from app.core.database import Base
from app.core.logging import db_logger
from app.core.metrics import api_metrics
import time

T = TypeVar('T', bound=Base)


class IRepository(ABC):
    """Interface for repository pattern (Interface Segregation Principle)"""
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        pass
    
    @abstractmethod
    def update(self, id: str, **kwargs) -> Optional[T]:
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        pass


class BaseRepository(IRepository):
    """
    Base repository implementation following Single Responsibility Principle
    Handles common CRUD operations for all models
    """
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
        self.table_name = model.__tablename__
    
    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID with metrics and logging"""
        start_time = time.time()
        try:
            result = self.db.query(self.model).filter(self.model.id == id).first()
            duration_ms = (time.time() - start_time) * 1000
            
            db_logger.log_query("SELECT", self.table_name, duration_ms)
            api_metrics.record_database_operation("SELECT", self.table_name, duration_ms, True)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("SELECT", self.table_name, str(e))
            api_metrics.record_database_operation("SELECT", self.table_name, duration_ms, False)
            raise
    
    def get_all(self) -> List[T]:
        """Get all entities with metrics and logging"""
        start_time = time.time()
        try:
            result = self.db.query(self.model).all()
            duration_ms = (time.time() - start_time) * 1000
            
            db_logger.log_query("SELECT_ALL", self.table_name, duration_ms, count=len(result))
            api_metrics.record_database_operation("SELECT_ALL", self.table_name, duration_ms, True)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("SELECT_ALL", self.table_name, str(e))
            api_metrics.record_database_operation("SELECT_ALL", self.table_name, duration_ms, False)
            raise
    
    def create(self, **kwargs) -> T:
        """Create new entity with metrics and logging"""
        start_time = time.time()
        try:
            db_obj = self.model(**kwargs)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_query("INSERT", self.table_name, duration_ms, entity_id=db_obj.id)
            api_metrics.record_database_operation("INSERT", self.table_name, duration_ms, True)
            
            return db_obj
        except Exception as e:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("INSERT", self.table_name, str(e))
            api_metrics.record_database_operation("INSERT", self.table_name, duration_ms, False)
            raise
    
    def update(self, id: str, **kwargs) -> Optional[T]:
        """Update entity with metrics and logging"""
        start_time = time.time()
        try:
            db_obj = self.get_by_id(id)
            if db_obj:
                for field, value in kwargs.items():
                    if value is not None:  # Only update non-None values
                        setattr(db_obj, field, value)
                
                self.db.commit()
                self.db.refresh(db_obj)
                
                duration_ms = (time.time() - start_time) * 1000
                db_logger.log_query("UPDATE", self.table_name, duration_ms, entity_id=id)
                api_metrics.record_database_operation("UPDATE", self.table_name, duration_ms, True)
                
                return db_obj
            return None
        except Exception as e:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("UPDATE", self.table_name, str(e), entity_id=id)
            api_metrics.record_database_operation("UPDATE", self.table_name, duration_ms, False)
            raise
    
    def delete(self, id: str) -> bool:
        """Delete entity with metrics and logging"""
        start_time = time.time()
        try:
            db_obj = self.get_by_id(id)
            if db_obj:
                self.db.delete(db_obj)
                self.db.commit()
                
                duration_ms = (time.time() - start_time) * 1000
                db_logger.log_query("DELETE", self.table_name, duration_ms, entity_id=id)
                api_metrics.record_database_operation("DELETE", self.table_name, duration_ms, True)
                
                return True
            return False
        except Exception as e:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("DELETE", self.table_name, str(e), entity_id=id)
            api_metrics.record_database_operation("DELETE", self.table_name, duration_ms, False)
            raise
    
    def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Get entity by specific field"""
        start_time = time.time()
        try:
            field = getattr(self.model, field_name)
            result = self.db.query(self.model).filter(field == value).first()
            
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_query("SELECT_BY_FIELD", self.table_name, duration_ms, field=field_name)
            api_metrics.record_database_operation("SELECT_BY_FIELD", self.table_name, duration_ms, True)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("SELECT_BY_FIELD", self.table_name, str(e), field=field_name)
            api_metrics.record_database_operation("SELECT_BY_FIELD", self.table_name, duration_ms, False)
            raise
    
    def filter_by(self, **filters) -> List[T]:
        """Filter entities by multiple criteria"""
        start_time = time.time()
        try:
            query = self.db.query(self.model)
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.filter(field == value)
            
            result = query.all()
            
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_query("FILTER", self.table_name, duration_ms, count=len(result), filters=filters)
            api_metrics.record_database_operation("FILTER", self.table_name, duration_ms, True)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.log_error("FILTER", self.table_name, str(e), filters=filters)
            api_metrics.record_database_operation("FILTER", self.table_name, duration_ms, False)
            raise
