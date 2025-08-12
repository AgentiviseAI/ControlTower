"""
MCP Tools API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import MCPTool, MCPToolCreate, MCPToolUpdate, ListResponse
from app.services import MCPToolService
from app.api.dependencies import get_mcp_tool_service
from app.core.exceptions import NotFoundError, ConflictError
from app.middleware.authorization import (
    RequireMCPCreate, RequireMCPRead, RequireMCPUpdate, RequireMCPDelete
)

router = APIRouter(prefix="/mcp-tools", tags=["MCP Tools"])


@router.get("", response_model=ListResponse)
async def list_mcp_tools(
    auth: tuple = Depends(RequireMCPRead),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """List all MCP tools for the current organization"""
    user_id, organization_id = auth
    tools = mcp_service.list_tools(organization_id)
    return ListResponse(items=tools, total=len(tools))


@router.post("", response_model=MCPTool, status_code=status.HTTP_201_CREATED)
async def create_mcp_tool(
    tool: MCPToolCreate,
    auth: tuple = Depends(RequireMCPCreate),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Register a new MCP tool"""
    user_id, organization_id = auth
    try:
        created_tool = mcp_service.create_tool(
            organization_id=organization_id,
            **tool.dict()
        )
        return created_tool
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{tool_id}", response_model=MCPTool)
async def get_mcp_tool(
    tool_id: str,
    auth: tuple = Depends(RequireMCPRead),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Get a specific MCP tool"""
    user_id, organization_id = auth
    try:
        tool = mcp_service.get_tool(tool_id)
        return tool
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{tool_id}", response_model=MCPTool)
async def update_mcp_tool(
    tool_id: str,
    tool: MCPToolUpdate,
    auth: tuple = Depends(RequireMCPUpdate),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Update MCP tool configuration"""
    user_id, organization_id = auth
    try:
        tool_data = tool.dict(exclude_unset=True)
        updated_tool = mcp_service.update_tool(tool_id, **tool_data)
        return updated_tool
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_tool(
    tool_id: str,
    auth: tuple = Depends(RequireMCPDelete),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Unregister an MCP tool"""
    user_id, organization_id = auth
    try:
        mcp_service.delete_tool(tool_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{tool_id}/test", response_model=dict)
async def test_mcp_tool(
    tool_id: str,
    auth: tuple = Depends(RequireMCPRead),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Test MCP tool connectivity and functionality"""
    user_id, organization_id = auth
    try:
        result = mcp_service.test_tool_connection(tool_id)
        return {"status": "success", "result": result}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tool test failed: {str(e)}")


@router.post("/{tool_id}/execute", response_model=dict)
async def execute_mcp_tool(
    tool_id: str,
    parameters: dict,
    auth: tuple = Depends(RequireMCPRead),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Execute an MCP tool with given parameters"""
    user_id, organization_id = auth
    try:
        result = mcp_service.execute_tool(tool_id, parameters)
        return {"status": "success", "result": result}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tool execution failed: {str(e)}")


@router.get("/{tool_id}/schema", response_model=dict)
async def get_mcp_tool_schema(
    tool_id: str,
    auth: tuple = Depends(RequireMCPRead),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service)
):
    """Get the input/output schema for an MCP tool"""
    user_id, organization_id = auth
    try:
        schema = mcp_service.get_tool_schema(tool_id)
        return {"tool_id": tool_id, "schema": schema}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
