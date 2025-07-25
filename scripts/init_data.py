"""
Initialize database with sample data
"""
from app.core.database import get_db, create_tables
from app.services import AIAgentService, MCPToolService, LLMService, RAGConnectorService, SecurityService, WorkflowService
from app.repositories import (
    AIAgentRepository, MCPToolRepository, LLMRepository, 
    RAGConnectorRepository, SecurityRoleRepository, UserRepository, WorkflowRepository
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
        workflow_repo = WorkflowRepository(db)
        
        # Initialize services
        workflow_service = WorkflowService(workflow_repo, llm_repo)
        agent_service = AIAgentService(agent_repo, workflow_service)
        llm_service = LLMService(llm_repo)
        tool_service = MCPToolService(tool_repo)
        rag_service = RAGConnectorService(rag_repo)
        security_service = SecurityService(role_repo, user_repo)
        
        # Check if data already exists
        if agent_repo.get_all():
            print("Sample data already exists, skipping initialization")
            return
        
        print("Initializing sample data...")
        
        # Create sample LLMs first (so they can be linked to agents)
        # Azure AI Foundry Example
        llm_service.create_llm(
            name="GPT-4 Turbo (Azure AI Foundry)",
            description="GPT-4 Turbo model deployed on Azure AI Foundry",
            hosting_environment="azure_ai_foundry",
            azure_endpoint_url="https://my-ai-studio.inference.ai.azure.com",
            azure_api_key="your-azure-api-key",
            azure_deployment_name="gpt-4-turbo-deployment",
            model_name="gpt-4-turbo",
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9,
            enabled=True,
            status="active",
            usage_stats={
                "requests_today": 245,
                "tokens_used": 15420,
                "rate_limit": 1000
            }
        )
        
        # AWS Bedrock Example
        llm_service.create_llm(
            name="Claude 3 Sonnet (AWS Bedrock)",
            description="Claude 3 Sonnet via AWS Bedrock",
            hosting_environment="aws_bedrock",
            aws_region="us-east-1",
            aws_access_key_id="your-aws-access-key",
            aws_secret_access_key="your-aws-secret-key",
            aws_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_name="claude-3-sonnet",
            temperature=0.3,
            max_tokens=4096,
            enabled=True,
            status="active",
            usage_stats={
                "requests_today": 189,
                "tokens_used": 12340,
                "rate_limit": 800
            }
        )
        
        # Google Cloud Vertex AI Example
        llm_service.create_llm(
            name="Gemini Pro (Vertex AI)",
            description="Gemini Pro model via Google Cloud Vertex AI",
            hosting_environment="gcp_vertex_ai",
            gcp_project_id="my-gcp-project-123",
            gcp_region="us-central1",
            gcp_auth_method="adc",
            gcp_model_type="foundation",
            gcp_model_name="gemini-1.5-pro",
            model_name="gemini-1.5-pro",
            temperature=0.8,
            max_tokens=8192,
            enabled=True,
            status="active",
            usage_stats={
                "requests_today": 567,
                "tokens_used": 45230,
                "rate_limit": 2000
            }
        )
        
        # Custom Deployment (OpenAI-compatible API) Example
        llm_service.create_llm(
            name="Gemma 2 2B (Self-hosted)",
            description="Self-hosted Gemma 2 2B with OpenAI-compatible API",
            hosting_environment="custom_deployment",
            custom_deployment_location="on_premise",
            custom_llm_provider="Google (Gemma)",
            custom_api_endpoint_url="http://135.236.105.112:11434/api/generate",
            custom_api_compatibility="ollama_compatible",
            custom_auth_method="api_key_header",
            custom_auth_header_name="Authorization",
            custom_auth_key_prefix="Bearer ",
            custom_auth_api_key="your-local-api-key",
            model_name="gemma-2-2b-instruct",
            temperature=0.7,
            max_tokens=2048,
            top_p=0.95,
            stop_sequences="<|im_end|>,<|endoftext|>",
            enabled=True,
            status="active",
            usage_stats={
                "requests_today": 95,
                "tokens_used": 8540,
                "rate_limit": 500
            }
        )
        
        # AWS SageMaker Example
        llm_service.create_llm(
            name="Custom Fine-tuned Model (SageMaker)",
            description="Custom fine-tuned model deployed on AWS SageMaker",
            hosting_environment="aws_sagemaker",
            aws_region="us-west-2",
            aws_access_key_id="your-aws-access-key",
            aws_secret_access_key="your-aws-secret-key",
            aws_sagemaker_endpoint_name="my-custom-model-endpoint",
            aws_content_handler_class="my_handlers.CustomLlamaHandler",
            model_name="custom-llama-finance",
            temperature=0.5,
            max_tokens=2048,
            enabled=True,
            status="active",
            usage_stats={
                "requests_today": 42,
                "tokens_used": 3420,
                "rate_limit": 200
            }
        )
        
        # Create sample AI Agents (after LLMs so they can be linked)
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
                "workflows": ["create", "read", "update", "delete", "deploy"],
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
                "workflows": ["create", "read", "update", "delete"],
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
                "workflows": ["read"],
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
