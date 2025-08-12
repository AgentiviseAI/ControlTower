# Transaction Middleware Usage Guide

The transaction middleware provides atomic database operations for FastAPI endpoints, ensuring that complex operations either succeed completely or fail completely (all-or-nothing).

## Features

- **Atomic Operations**: All database changes within a transaction are committed together or rolled back together
- **Error Handling**: Proper handling of database constraints, data validation, and business logic errors
- **Reusable**: Can be applied to any endpoint that needs transactional behavior
- **Logging**: Comprehensive logging for debugging and monitoring

## Usage Examples

### 1. Complex Multi-Step Operations (Recommended)

Use `TransactionManager` for operations involving multiple services or complex logic:

```python
@router.post("/agents", response_model=AIAgent)
async def create_agent_with_workflow(
    agent: AIAgentCreate,
    agent_service: AIAgentService = Depends(get_ai_agent_service),
    workflow_service: WorkflowService = Depends(get_workflow_service),
    transaction_manager: TransactionManager = Depends(get_transaction_manager)
):
    def atomic_operation():
        # Step 1: Create agent
        created_agent = agent_service.create_agent(...)
        
        # Step 2: Create workflow
        workflow = workflow_service.create_workflow(
            agent_id=created_agent['id'], ...
        )
        
        # Step 3: Update agent with workflow
        updated_agent = agent_service.update_agent(
            agent_id=created_agent['id'],
            workflow_id=workflow['id']
        )
        
        return updated_agent
    
    return transaction_manager.execute_atomic([atomic_operation])
```

### 2. Simple Operations with Decorator

Use `@atomic_operation` decorator for simpler cases:

```python
@router.post("/simple-resource")
@atomic_operation
async def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    # All database operations here are atomic
    main_resource = service.create_main_resource(db, resource)
    related_resource = service.create_related_resource(db, main_resource.id)
    return main_resource
```

### 3. Manual Transaction Control

For fine-grained control:

```python
@router.post("/manual-transaction")
async def manual_transaction_example(
    db: Session = Depends(get_db)
):
    with db_transaction(db):
        # All operations within this block are atomic
        resource1 = service.create_resource1(db)
        resource2 = service.create_resource2(db, resource1.id)
        return {"resource1": resource1, "resource2": resource2}
```

## Error Handling

The middleware handles various error types:

- **ConflictError**: Business logic conflicts (409 Conflict)
- **IntegrityError**: Database constraint violations (409 Conflict)
- **DataError**: Invalid data format (400 Bad Request)
- **SQLAlchemyError**: General database errors (500 Internal Server Error)
- **HTTPException**: Re-raised as-is
- **Other Exceptions**: Wrapped as 500 Internal Server Error

## Best Practices

1. **Use TransactionManager for complex operations** involving multiple services
2. **Keep transactions short** to avoid long-running locks
3. **Handle specific exceptions** at the business logic level when possible
4. **Test rollback scenarios** to ensure data consistency
5. **Monitor transaction performance** and optimize slow operations

## Integration

The middleware is automatically available through dependency injection:

```python
from app.middleware import get_transaction_manager, atomic_operation, db_transaction
```

## Logging

All transaction operations are logged with appropriate levels:
- **DEBUG**: Transaction start/commit
- **WARNING**: Business logic conflicts
- **ERROR**: Database and system errors
