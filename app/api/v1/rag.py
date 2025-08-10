"""
RAG Connector API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import RAGConnector, RAGConnectorCreate, RAGConnectorUpdate, ListResponse
from app.services import RAGConnectorService
from app.api.dependencies import get_rag_connector_service, get_current_user_id, get_current_organization_id
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/rag", tags=["RAG Connectors"])


@router.get("/connectors", response_model=ListResponse)
async def list_rag_connectors(
    user_id: str = Depends(get_current_user_id),
    organization_id: str = Depends(get_current_organization_id),
    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """List all RAG connectors for the current organization"""
    connectors = rag_service.list_connectors(organization_id)
    return ListResponse(items=connectors, total=len(connectors))


@router.post("/connectors", response_model=RAGConnector, status_code=status.HTTP_201_CREATED)
async def create_rag_connector(
    connector: RAGConnectorCreate,
    user_id: str = Depends(get_current_user_id),
    organization_id: str = Depends(get_current_organization_id),
    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Create a new RAG connector"""
    try:
        created_connector = rag_service.create_connector(
            organization_id=organization_id,
            **connector.dict()
        )
        return created_connector
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/connectors/{connector_id}", response_model=RAGConnector)
async def get_rag_connector(
    connector_id: str,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Get a specific RAG connector"""
    try:
        connector = rag_service.get_connector(connector_id)
        return connector
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/connectors/{connector_id}", response_model=RAGConnector)
async def update_rag_connector(
    connector_id: str,
    connector: RAGConnectorUpdate,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Update RAG connector configuration"""
    try:
        connector_data = connector.dict(exclude_unset=True)
        updated_connector = rag_service.update_connector(connector_id, **connector_data)
        return updated_connector
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/connectors/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rag_connector(
    connector_id: str,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Delete a RAG connector"""
    try:
        rag_service.delete_connector(connector_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/connectors/{connector_id}/test", response_model=dict)
async def test_rag_connector(
    connector_id: str,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Test RAG connector connectivity"""
    try:
        result = rag_service.test_connector_connection(connector_id)
        return {"status": "success", "result": result}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Connection test failed: {str(e)}")


@router.post("/connectors/{connector_id}/index", response_model=dict)
async def create_index(
    connector_id: str,
    index_config: dict,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Create a new index in the RAG connector"""
    try:
        result = rag_service.create_index(connector_id, index_config)
        return {"status": "success", "result": result}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Index creation failed: {str(e)}")


@router.post("/connectors/{connector_id}/search", response_model=dict)
async def search_documents(
    connector_id: str,
    search_query: dict,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Search documents in the RAG connector"""
    try:
        results = rag_service.search_documents(connector_id, search_query)
        return {"status": "success", "results": results}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search failed: {str(e)}")


@router.post("/connectors/{connector_id}/documents", response_model=dict)
async def add_documents(
    connector_id: str,
    documents: List[dict],

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Add documents to the RAG connector"""
    try:
        result = rag_service.add_documents(connector_id, documents)
        return {"status": "success", "result": result}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Document addition failed: {str(e)}")


@router.get("/connectors/{connector_id}/stats", response_model=dict)
async def get_connector_stats(
    connector_id: str,

    rag_service: RAGConnectorService = Depends(get_rag_connector_service)
):
    """Get RAG connector statistics"""
    try:
        stats = rag_service.get_connector_stats(connector_id)
        return {"connector_id": connector_id, "stats": stats}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/metrics-config", response_model=dict)
async def get_rag_metrics_config():
    """Get RAG metrics configuration"""
    # Return default RAG metrics configuration
    return {
        "enabled": True,
        "metrics": {
            "query_latency": {"enabled": True, "threshold_ms": 1000},
            "search_accuracy": {"enabled": True, "threshold": 0.8},
            "document_relevance": {"enabled": True, "threshold": 0.7},
            "index_size": {"enabled": True, "max_documents": 100000},
            "memory_usage": {"enabled": True, "threshold_mb": 512}
        },
        "collection_interval": 60,
        "retention_days": 30
    }
