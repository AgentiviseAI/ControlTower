"""
Workflow Service implementation
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.repositories import WorkflowRepository, LLMRepository, MCPToolRepository, RAGConnectorRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class WorkflowService(BaseService):
    """Service for Workflow business logic"""
    
    def __init__(self, repository: WorkflowRepository, 
                 llm_repository: LLMRepository = None, 
                 mcp_repository: MCPToolRepository = None, 
                 rag_repository: RAGConnectorRepository = None):
        super().__init__(repository)
        self.llm_repository = llm_repository
        self.mcp_repository = mcp_repository
        self.rag_repository = rag_repository
    
    def create_workflow(self, organization_id: UUID, name: str, description: str = None, 
                       agent_id: str = None,
                       nodes: List[Dict[str, Any]] = None, 
                       edges: List[Dict[str, Any]] = None,
                       status: str = "draft",
                       is_default: bool = False,
                       execution_order: int = 1) -> Dict[str, Any]:
        """Create a new workflow (automatically detects transaction context)"""
        self._validate_data({'name': name}, ['name'])
        
        # Check if workflow with same name exists in this organization
        existing_workflow = self.repository.get_by_name_and_organization(name, organization_id)
        if existing_workflow:
            raise ConflictError(f"Workflow with name '{name}' already exists in this organization")
        
        self.logger.info(f"Creating workflow: {name} for organization: {organization_id}")
        
        # If no nodes/edges provided, create default start->end structure
        if not nodes or not edges:
            import uuid
            
            # Generate UUIDs for default nodes
            start_node_id = str(uuid.uuid4())
            end_node_id = str(uuid.uuid4())
            
            # Create default nodes
            default_nodes = [
                {
                    "id": start_node_id,
                    "label": "Start Here",
                    "type": "start",
                    "link": None,
                    "position": {"x": 100, "y": 100},
                    "config": {"message": "Start here"}
                },
                {
                    "id": end_node_id,
                    "label": "End Here",
                    "type": "end",
                    "link": None,
                    "position": {"x": 300, "y": 100},
                    "config": {"message": "End here"}
                }
            ]
            
            # Create default edges
            default_edges = [
                {
                    "source": start_node_id,
                    "target": end_node_id
                }
            ]
            
            # Use provided nodes/edges if available, otherwise use defaults
            nodes = nodes if nodes else default_nodes
            edges = edges if edges else default_edges
            
            self.logger.info(f"Creating workflow with default start->end structure for: {name}")
        
        workflow = self.repository.create(
            name=name,
            description=description,
            agent_id=agent_id,
            nodes=nodes,
            edges=edges,
            status=status,
            organization_id=organization_id,
            is_default=is_default,
            execution_order=execution_order
        )
        
        return self._workflow_to_dict(workflow)
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        workflow = self.repository.get_by_id(workflow_id)
        if not workflow:
            raise NotFoundError("Workflow", workflow_id)
        return self._workflow_to_dict(workflow)
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows"""
        workflows = self.repository.get_all()
        return [self._workflow_to_dict(workflow) for workflow in workflows]
    
    def list_workflows(self, organization_id: UUID) -> List[Dict[str, Any]]:
        """Get all workflows for a specific organization"""
        workflows = self.repository.get_by_organization(organization_id)
        return [self._workflow_to_dict(workflow) for workflow in workflows]
    
    def update_workflow(self, workflow_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update workflow"""
        self.logger.info(f"Updating workflow: {workflow_id}")
        
        workflow = self.repository.update(workflow_id, **kwargs)
        if not workflow:
            raise NotFoundError("Workflow", workflow_id)
        
        return self._workflow_to_dict(workflow)
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        self.logger.info(f"Deleting workflow: {workflow_id}")
        
        success = self.repository.delete(workflow_id)
        if not success:
            raise NotFoundError("Workflow", workflow_id)
        
        return success
    
    def get_node_options(self) -> Dict[str, Any]:
        """Get available options for workflow nodes"""
        options = {
            "llms": [],
            "mcp_tools": [],
            "rag_connectors": []
        }
        
        try:
            # Get LLMs
            if self.llm_repository:
                llms = self.llm_repository.get_all()
                options["llms"] = [
                    {
                        "id": llm.id,
                        "name": llm.name,
                        "model_name": llm.model_name,
                        "hosting_environment": llm.hosting_environment,
                        "enabled": llm.enabled
                    } for llm in llms if llm.enabled
                ]
            
            # Get MCP Tools
            if self.mcp_repository:
                tools = self.mcp_repository.get_all()
                options["mcp_tools"] = [
                    {
                        "id": tool.id,
                        "name": tool.name,
                        "description": tool.description,
                        "endpoint_url": tool.endpoint_url,
                        "enabled": tool.enabled
                    } for tool in tools if tool.enabled
                ]
            
            # Get RAG Connectors
            if self.rag_repository:
                connectors = self.rag_repository.get_all()
                options["rag_connectors"] = [
                    {
                        "id": connector.id,
                        "name": connector.name,
                        "type": connector.type,
                        "configured": connector.configured,
                        "enabled": connector.enabled
                    } for connector in connectors if connector.enabled and connector.configured
                ]
                
        except Exception as e:
            self.logger.error(f"Error fetching node options: {e}")
            # Return empty options on error, don't fail the request
            
        return options
    
    def _workflow_to_dict(self, workflow) -> Dict[str, Any]:
        """Convert workflow to dict with proper node handling"""
        if not workflow:
            return None
        
        result = self._to_dict(workflow)
        # Ensure nodes are properly formatted
        if 'nodes' in result and result['nodes']:
            # Convert components to nodes format for compatibility
            result['nodes'] = result['nodes']
        
        return result
    
    def create_default_workflow(self, agent_id: str, agent_name: str = None) -> Dict[str, Any]:
        """Create a default workflow for an agent with proper LLM linking"""
        import uuid
        
        # Generate UUIDs for nodes
        start_node_id = str(uuid.uuid4())
        end_node_id = str(uuid.uuid4())
        
        # Use agent_name if provided, otherwise generate a generic name
        workflow_name = f"{agent_name} - Default Workflow" if agent_name else f"Default Workflow - {uuid.uuid4().hex[:8]}"
        workflow_description = f"Default workflow for agent {agent_name}" if agent_name else "Default workflow with intelligent LLM integration"
        
        # Check if 'Gemma 2 2B (Self-hosted)' LLM exists
        gemma_llm_id = None
        try:
            if self.llm_repository:
                all_llms = self.llm_repository.get_all()
                for llm in all_llms:
                    if llm.name == 'Gemma 2 2B (Self-hosted)':
                        gemma_llm_id = llm.id
                        break
        except Exception as e:
            self.logger.warning(f"Could not check for 'Gemma 2 2B (Self-hosted)' LLM: {e}")
        
        # Create workflow based on whether Gemma LLM exists
        if gemma_llm_id:
            # Create 3-node workflow: start -> llm -> end
            llm_node_id = str(uuid.uuid4())
            nodes = [
                {
                    "id": start_node_id,
                    "label": "Start",
                    "type": "start",
                    "link": None,
                    "position": {"x": 100, "y": 100},
                    "config": {"message": "Start here"}
                },
                {
                    "id": llm_node_id,
                    "label": "LLM",
                    "type": "llm",
                    "link": gemma_llm_id,
                    "position": {"x": 300, "y": 100}, 
                    "config": {"model": "gemma-2-2b-instruct", "temperature": 0.7}
                },
                {
                    "id": end_node_id,
                    "label": "End",
                    "type": "end",
                    "link": None,
                    "position": {"x": 500, "y": 100},
                    "config": {"message": "End here"}
                }
            ]
            edges = [
                {
                    "source": start_node_id,
                    "target": llm_node_id
                },
                {
                    "source": llm_node_id,
                    "target": end_node_id
                }
            ]
            self.logger.info(f"Creating default workflow with 'Gemma 2 2B (Self-hosted)' LLM linked for agent {agent_id}")
        else:
            # Create 2-node workflow: start -> end (no LLM available)
            nodes = [
                {
                    "id": start_node_id,
                    "label": "Start",
                    "type": "start",
                    "link": None,
                    "position": {"x": 100, "y": 100},
                    "config": {"message": "Start here"}
                },
                {
                    "id": end_node_id,
                    "label": "End",
                    "type": "end",
                    "link": None,
                    "position": {"x": 300, "y": 100},
                    "config": {"message": "End here"}
                }
            ]
            edges = [
                {
                    "source": start_node_id,
                    "target": end_node_id
                }
            ]
            self.logger.info(f"Creating simple start->end workflow (no 'Gemma 2 2B (Self-hosted)' LLM found) for agent {agent_id}")
        
        # Create the workflow
        return self.create_workflow(
            name=workflow_name,
            description=workflow_description,
            agent_id=agent_id,  # Link the workflow to the agent
            nodes=nodes,
            edges=edges,
            status="draft"
        )
    
    def get_default_workflow_for_agent(self, agent_id: str, organization_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the default workflow for an agent"""
        workflows = self.repository.get_by_agent_id(agent_id)
        
        # Filter by organization and find the default workflow
        for workflow in workflows:
            if workflow.organization_id == organization_id and getattr(workflow, 'is_default', False):
                return self._workflow_to_dict(workflow)
        
        return None
    
    def get_workflows_for_agent(self, agent_id: str, organization_id: UUID) -> List[Dict[str, Any]]:
        """Get all workflows for an agent, ordered by execution order"""
        workflows = self.repository.get_by_agent_id(agent_id)
        
        # Filter by organization and sort by execution order
        org_workflows = [w for w in workflows if w.organization_id == organization_id]
        org_workflows.sort(key=lambda w: getattr(w, 'execution_order', 999))
        
        return [self._workflow_to_dict(workflow) for workflow in org_workflows]
    