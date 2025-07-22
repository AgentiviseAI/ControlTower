"""
Initialize database with sample data
"""
from app.core.database import get_db, create_tables
from app.services import AIAgentService, MCPToolService, LLMService, RAGConnectorService, SecurityService, PipelineService
from app.repositories import (
    AIAgentRepository, MCPToolRepository, LLMRepository, 
    RAGConnectorRepository, SecurityRoleRepository, UserRepository, PipelineRepository
)
from datetime import datetime


def initialize_sample_data():
    """Initialize the database with sample data"""
    
    # Create all tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize repositories
        agent_repo = AIAgentRepository(db)
        tool_repo = MCPToolRepository(db)
        llm_repo = LLMRepository(db)
        rag_repo = RAGConnectorRepository(db)
        role_repo = SecurityRoleRepository(db)
        user_repo = UserRepository(db)
        pipeline_repo = PipelineRepository(db)
        
        # Initialize services
        pipeline_service = PipelineService(pipeline_repo)
        agent_service = AIAgentService(agent_repo, pipeline_service)
        tool_service = MCPToolService(tool_repo)
        llm_service = LLMService(llm_repo)
        rag_service = RAGConnectorService(rag_repo)
        security_service = SecurityService(role_repo, user_repo)
        
        # Check if data already exists
        if agent_repo.get_all():
            print("Sample data already exists, skipping initialization")
            return
        
        print("Initializing sample data...")
        
        # Create sample AI Agents
        agent_service.create_agent(
            name="Customer Support Agent",
            description="Handles customer inquiries and support requests",
            enabled=True,
            preview_enabled=True
        )
        
        agent_service.create_agent(
            name="Data Analysis Agent",
            description="Analyzes data and generates insights",
            enabled=True,
            preview_enabled=False
        )
        
        # Create sample MCP Tools
        tool_service.create_tool(
            name="Database Connector",
            description="Connects to SQL databases",
            enabled=True,
            endpoint_url="https://api.example.com/db-connector",
            status="active",
            required_permissions=["read", "write"],
            auth_headers={"X-API-Key": "demo_key"}
        )
        
        tool_service.create_tool(
            name="Email Service",
            description="Sends and manages emails",
            enabled=False,
            endpoint_url="https://api.example.com/email-service",
            status="inactive",
            required_permissions=["send"],
            auth_headers={}
        )
        
        # Create sample LLMs
        llm_service.create_llm(
            name="Primary Chat Model",
            model_name="Llama 3 8B",
            provider="Meta",
            enabled=True,
            endpoint_url="https://api.example.com/llama3-8b",
            status="active",
            usage_stats={
                "requests_today": 245,
                "tokens_used": 15420,
                "rate_limit": 1000
            },
            config={
                "temperature": 0.7,
                "max_tokens": 2048
            }
        )
        
        llm_service.create_llm(
            name="Code Generation Model",
            model_name="Mixtral 8x7B",
            provider="Anthropic",
            enabled=True,
            endpoint_url="https://api.example.com/mixtral-8x7b",
            status="active",
            usage_stats={
                "requests_today": 189,
                "tokens_used": 12340,
                "rate_limit": 800
            },
            config={
                "temperature": 0.3,
                "max_tokens": 4096
            }
        )
        
        llm_service.create_llm(
            name="GPT-4 Turbo",
            model_name="gpt-4-turbo",
            provider="OpenAI",
            enabled=True,
            endpoint_url="https://api.openai.com/v1/chat/completions",
            status="active",
            usage_stats={
                "requests_today": 567,
                "tokens_used": 45230,
                "rate_limit": 2000
            },
            config={
                "temperature": 0.8,
                "max_tokens": 8192
            }
        )
        
        # Create sample RAG Connectors
        rag_service.create_connector(
            name="Wiki",
            type="wiki",
            enabled=True,
            connection_details={"url": "https://wiki.example.com", "api_key": "wiki_key_123"}
        )
        
        rag_service.create_connector(
            name="Confluence",
            type="confluence",
            enabled=False,
            connection_details={}
        )
        
        rag_service.create_connector(
            name="Databases",
            type="database",
            enabled=True,
            connection_details={"connection_string": "postgresql://user:pass@localhost:5432/db"}
        )
        
        # Create sample security roles
        role_repo.create(
            name="Admin",
            description="Full system administrator with all permissions",
            status="active",
            permissions={
                "agents": ["create", "read", "update", "delete", "execute"],
                "llms": ["create", "read", "update", "delete", "configure"],
                "tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["create", "read", "update", "delete", "configure"],
                "pipelines": ["create", "read", "update", "delete", "deploy"],
                "metrics": ["read", "configure"],
                "security": ["read", "configure", "manage_users", "manage_roles"]
            }
        )
        
        role_repo.create(
            name="Developer",
            description="Development team member with limited administrative access",
            status="active",
            permissions={
                "agents": ["create", "read", "update", "delete", "execute"],
                "llms": ["read", "configure"],
                "tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["read", "update", "configure"],
                "pipelines": ["create", "read", "update", "delete"],
                "metrics": ["read"],
                "security": ["read"]
            }
        )
        
        role_repo.create(
            name="User",
            description="Standard user with read-only access to most features",
            status="active",
            permissions={
                "agents": ["read", "execute"],
                "llms": ["read"],
                "tools": ["read"],
                "rag": ["read"],
                "pipelines": ["read"],
                "metrics": ["read"],
                "security": []
            }
        )
        
        # Create sample users
        user_repo.create(
            username="admin",
            password="password",  # In real app, hash this
            name="John Admin",
            email="john@company.com",
            role="Admin",
            status="active"
        )
        
        user_repo.create(
            username="user",
            password="password",  # In real app, hash this
            name="Jane User",
            email="jane@company.com",
            role="User",
            status="active"
        )
        
        print("Sample data initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    initialize_sample_data()
