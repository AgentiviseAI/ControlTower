"""
API v1 router configuration
"""
from fastapi import APIRouter
from . import agents, security, workflows, llms, mcp, rag

# Create the main v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(agents.router)
api_router.include_router(security.router)
api_router.include_router(workflows.router)
api_router.include_router(llms.router)
api_router.include_router(mcp.router)
api_router.include_router(rag.router)
