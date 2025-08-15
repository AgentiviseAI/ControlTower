"""
REST API management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from uuid import UUID

from app.api.dependencies import get_rest_api_service
from app.services.rest_api_service import RestAPIService
from app.middleware.authorization import (
    RequireRestAPICreate, RequireRestAPIRead, RequireRestAPIUpdate, RequireRestAPIDelete
)
from app.schemas.rest_api import (
    RestAPICreateRequest, RestAPIUpdateRequest, RestAPIResponse,
    RestAPIBulkCreateRequest, RestAPIBulkDeleteRequest,
    RestAPIFromOpenAPIRequest, RestAPIListResponse,
    RestAPIBulkCreateResponse, RestAPIBulkDeleteResponse,
    RestAPIQueryParams, HTTPMethod, RestAPIStatus
)

router = APIRouter(prefix="/rest-apis", tags=["REST APIs"])


@router.post("/", response_model=RestAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_rest_api(
    api_data: RestAPICreateRequest,
    auth: tuple = Depends(RequireRestAPICreate),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Create a new REST API configuration"""
    user_id, organization_id = auth
    
    try:
        api = rest_api_service.create_api(
            organization_id=str(organization_id),
            **api_data.dict()
        )
        return RestAPIResponse(**api)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk", response_model=RestAPIBulkCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_multiple_rest_apis(
    bulk_data: RestAPIBulkCreateRequest,
    auth: tuple = Depends(RequireRestAPICreate),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Create multiple REST API configurations"""
    user_id, organization_id = auth
    
    try:
        apis_data = [api.dict() for api in bulk_data.apis]
        results = rest_api_service.create_multiple_apis(str(organization_id), apis_data)
        
        created = []
        failed = []
        
        for result in results:
            if "error" in result:
                failed.append({"name": result["name"], "error": result["error"]})
            else:
                created.append(RestAPIResponse(**result))
        
        return RestAPIBulkCreateResponse(
            created=created,
            failed=failed,
            total_requested=len(bulk_data.apis),
            total_created=len(created)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import/openapi", response_model=RestAPIBulkCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_from_openapi_spec(
    openapi_data: RestAPIFromOpenAPIRequest,
    background_tasks: BackgroundTasks,
    auth: tuple = Depends(RequireRestAPICreate),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Create REST APIs from OpenAPI/Swagger specification"""
    user_id, organization_id = auth
    
    try:
        # This is an async operation, so we could run it in the background
        results = await rest_api_service.create_from_openapi_spec(
            organization_id=str(organization_id),
            spec_url=str(openapi_data.spec_url),
            tags_to_attach=openapi_data.tags_filter
        )
        
        created = []
        failed = []
        
        for result in results:
            if "error" in result:
                failed.append({"name": result["name"], "error": result["error"]})
            else:
                created.append(RestAPIResponse(**result))
        
        return RestAPIBulkCreateResponse(
            created=created,
            failed=failed,
            total_requested=len(results),
            total_created=len(created)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=RestAPIListResponse)
async def list_rest_apis(
    auth: tuple = Depends(RequireRestAPIRead),
    rest_api_service: RestAPIService = Depends(get_rest_api_service),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    method: Optional[HTTPMethod] = Query(None, description="Filter by HTTP method"),
    api_status: Optional[RestAPIStatus] = Query(None, description="Filter by status"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    search: Optional[str] = Query(None, description="Search term for API names"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get all REST APIs for the current organization with optional filters"""
    user_id, organization_id = auth
    
    try:
        # Start with all APIs for the organization
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            apis = rest_api_service.list_apis_by_tags(str(organization_id), tag_list)
        else:
            apis = rest_api_service.list_apis(str(organization_id))
        
        # Apply filters
        if method:
            apis = [api for api in apis if api.get('method') == method.value]
        
        if api_status:
            apis = [api for api in apis if api.get('status') == api_status.value]
        
        if enabled is not None:
            apis = [api for api in apis if api.get('enabled') == enabled]
        
        if search:
            apis = [api for api in apis if search.lower() in api.get('name', '').lower()]
        
        # Apply pagination
        total = len(apis)
        apis = apis[offset:offset + limit]
        
        return RestAPIListResponse(
            items=[RestAPIResponse(**api) for api in apis],
            total=total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/all", response_model=RestAPIBulkDeleteResponse)
async def delete_all_rest_apis(
    auth: tuple = Depends(RequireRestAPIDelete),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Delete all REST API configurations for the current organization"""
    user_id, organization_id = auth
    
    try:
        # Get all APIs for the current organization
        all_apis = rest_api_service.list_apis(str(organization_id))
        
        if not all_apis:
            return RestAPIBulkDeleteResponse(
                deleted=[],
                failed=[],
                not_found=[],
                total_requested=0,
                total_deleted=0
            )
        
        # Extract all API IDs
        api_ids = [api['id'] for api in all_apis]
        
        # Delete all APIs
        results = rest_api_service.delete_multiple_apis(api_ids)
        
        return RestAPIBulkDeleteResponse(
            deleted=results["deleted"],
            failed=results["failed"],
            not_found=results["not_found"],
            total_requested=len(api_ids),
            total_deleted=len(results["deleted"])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/bulk", response_model=RestAPIBulkDeleteResponse)
async def delete_multiple_rest_apis(
    bulk_data: RestAPIBulkDeleteRequest,
    auth: tuple = Depends(RequireRestAPIDelete),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Delete multiple REST API configurations"""
    user_id, organization_id = auth
    
    try:
        # Verify all APIs belong to the current organization
        verified_api_ids = []
        not_found = []
        
        for api_id in bulk_data.api_ids:
            try:
                existing_api = rest_api_service.get_api(api_id)
                if existing_api.get('organization_id') == str(organization_id):
                    verified_api_ids.append(api_id)
                else:
                    not_found.append(api_id)
            except Exception:
                not_found.append(api_id)
        
        # Delete the verified APIs
        results = rest_api_service.delete_multiple_apis(verified_api_ids)
        
        # Add the not_found APIs to the results
        results["not_found"].extend(not_found)
        
        return RestAPIBulkDeleteResponse(
            deleted=results["deleted"],
            failed=results["failed"],
            not_found=results["not_found"],
            total_requested=len(bulk_data.api_ids),
            total_deleted=len(results["deleted"])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{api_id}", response_model=RestAPIResponse)
async def get_rest_api(
    api_id: str,
    auth: tuple = Depends(RequireRestAPIRead),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Get a specific REST API by ID"""
    user_id, organization_id = auth
    
    try:
        api = rest_api_service.get_api(api_id)
        
        # Verify the API belongs to the current organization
        if api.get('organization_id') != str(organization_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="REST API not found"
            )
        
        return RestAPIResponse(**api)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{api_id}", response_model=RestAPIResponse)
async def update_rest_api(
    api_id: str,
    api_data: RestAPIUpdateRequest,
    auth: tuple = Depends(RequireRestAPIUpdate),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Update a REST API configuration"""
    user_id, organization_id = auth
    
    try:
        # First verify the API exists and belongs to the organization
        existing_api = rest_api_service.get_api(api_id)
        if existing_api.get('organization_id') != str(organization_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="REST API not found"
            )
        
        # Update the API
        update_data = api_data.dict(exclude_unset=True)
        api = rest_api_service.update_api(api_id, **update_data)
        return RestAPIResponse(**api)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rest_api(
    api_id: str,
    auth: tuple = Depends(RequireRestAPIDelete),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
):
    """Delete a REST API configuration"""
    user_id, organization_id = auth
    
    try:
        # First verify the API exists and belongs to the organization
        existing_api = rest_api_service.get_api(api_id)
        if existing_api.get('organization_id') != str(organization_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="REST API not found"
            )
        
        # Delete the API
        rest_api_service.delete_api(api_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
