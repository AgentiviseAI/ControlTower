"""
IntentData API endpoints - Read-only operations
IntentData creation, updates, and deletions are handled internally by 
rest_api_service and mcp_tool_service
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.services.intent_data_service import IntentDataService
from app.repositories.intent_data_repository import IntentDataRepository
from app.schemas.intent_data import IntentDataResponse
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.middleware.authorization import RequireIntentDataRead

logger = get_logger(__name__)
router = APIRouter(prefix="/intent-data", tags=["Intent Data"])


def get_intent_data_service(db=Depends(get_db)) -> IntentDataService:
    """Dependency to get IntentData service"""
    repository = IntentDataRepository(db)
    return IntentDataService(repository)


@router.get("/", response_model=List[IntentDataResponse])
async def list_intent_data(
    enabled_only: Optional[bool] = Query(False, description="Filter to enabled intent data only"),
    source_type: Optional[str] = Query(None, description="Filter by source type (rest_api, mcp_tool)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    auth: tuple = Depends(RequireIntentDataRead),
    service: IntentDataService = Depends(get_intent_data_service)
):
    """List intent data records"""
    user_id, organization_id = auth
    try:
        if search:
            intent_data_list = service.search_intent_data(str(organization_id), search)
        elif source_type:
            intent_data_list = service.list_by_source_type(str(organization_id), source_type)
        elif category:
            intent_data_list = service.get_by_category(str(organization_id), category)
        else:
            intent_data_list = service.list_intent_data(str(organization_id), enabled_only)
        
        return intent_data_list
    except Exception as e:
        logger.error(f"Error listing intent data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{intent_data_id}", response_model=IntentDataResponse)
async def get_intent_data(
    intent_data_id: str,
    auth: tuple = Depends(RequireIntentDataRead),
    service: IntentDataService = Depends(get_intent_data_service)
):
    """Get intent data by ID"""
    user_id, organization_id = auth
    try:
        intent_data = service.get_intent_data(intent_data_id, str(organization_id))
        return intent_data
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting intent data {intent_data_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
