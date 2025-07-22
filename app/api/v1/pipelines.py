"""
Pipeline API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import Pipeline, PipelineCreate, PipelineUpdate, ListResponse
from app.services import PipelineService
from app.api.dependencies import get_pipeline_service, verify_token
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("", response_model=ListResponse)
async def list_pipelines(
    token: str = Depends(verify_token),
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """List all pipelines"""
    pipelines = pipeline_service.get_all_pipelines()
    return ListResponse(items=pipelines, total=len(pipelines))


@router.post("", response_model=Pipeline, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline: PipelineCreate,
    token: str = Depends(verify_token),
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Create a new pipeline"""
    try:
        # Convert the entire pipeline to dict first, then extract nested objects
        pipeline_dict = pipeline.dict()
        
        new_pipeline = pipeline_service.create_pipeline(
            name=pipeline_dict['name'],
            description=pipeline_dict.get('description'),
            nodes=pipeline_dict.get('nodes', []),
            edges=pipeline_dict.get('edges', []),
            status=pipeline_dict.get('status', 'draft')
        )
        return new_pipeline
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(
    pipeline_id: str,
    token: str = Depends(verify_token),
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Get a specific pipeline"""
    try:
        pipeline = pipeline_service.get_pipeline(pipeline_id)
        return pipeline
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{pipeline_id}", response_model=Pipeline)
async def update_pipeline(
    pipeline_id: str,
    pipeline: PipelineUpdate,
    token: str = Depends(verify_token),
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Update a pipeline"""
    try:
        # Convert Pydantic model to plain dict to avoid serialization issues
        update_data = pipeline.dict(exclude_unset=True)
        
        updated_pipeline = pipeline_service.update_pipeline(pipeline_id, **update_data)
        return updated_pipeline
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: str,
    token: str = Depends(verify_token),
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Delete a pipeline"""
    try:
        pipeline_service.delete_pipeline(pipeline_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
