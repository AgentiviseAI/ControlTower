"""
Workflow Component Definition model
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON
from app.models.base import BaseModel


class WorkflowComponentDefinition(BaseModel):
    """Model for workflow component definitions"""
    __tablename__ = "workflow_component_definitions"
    
    # Basic component info
    name = Column(String(255), nullable=False, index=True)
    component_id = Column(String(100), nullable=False, unique=True, index=True)  # e.g., 'llm', 'mcp_tool'
    category = Column(String(100), nullable=False, index=True)  # e.g., 'AI Models', 'Tools'
    description = Column(Text, nullable=True)
    
    # UI presentation
    icon_name = Column(String(100), nullable=True)  # Ant Design icon name
    color = Column(String(20), nullable=True)  # Hex color code
    
    # Component configuration
    config_schema = Column(JSON, nullable=True)  # JSON schema for configuration
    default_config = Column(JSON, nullable=True)  # Default configuration values
    
    # Component behavior
    input_ports = Column(JSON, nullable=True)  # Array of input port definitions
    output_ports = Column(JSON, nullable=True)  # Array of output port definitions
    
    # Metadata
    version = Column(String(20), nullable=True, default="1.0.0")
    tags = Column(JSON, nullable=True)  # Array of tags for categorization
    
    # Status and ordering
    enabled = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    
    # Implementation details
    implementation_class = Column(String(255), nullable=True)  # Python class for execution
    requirements = Column(JSON, nullable=True)  # Dependencies and requirements
    
    def __repr__(self):
        return f"<WorkflowComponentDefinition {self.component_id}: {self.name}>"
