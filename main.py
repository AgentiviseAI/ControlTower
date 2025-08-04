"""
Main application entry point with SOLID architecture
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, create_tables
from app.core.logging import setup_logging, get_logger
from app.middleware import LoggingMiddleware, MetricsMiddleware
from app.api.v1 import api_router
# Import models to ensure they're registered with SQLAlchemy
from app.models import AIAgent, MCPTool, LLM, RAGConnector, Workflow, SecurityRole, User, Metrics

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Platform application...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down AI Platform application...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="AI Platform API",
        description="A comprehensive platform for managing AI agents, LLMs, and workflows",
        version="1.0.0",
        lifespan=lifespan
    )

    origins = [
        "https://portal.agentiviseai.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Include routers
    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix
    )

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "AI Platform API",
            "version": "1.0.0",
            "status": "running"
        }

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app


# Create the application instance
app = create_application()

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )