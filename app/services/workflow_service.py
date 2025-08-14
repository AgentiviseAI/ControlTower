"""
Workflow Service implementation
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.repositories import WorkflowRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class WorkflowService(BaseService):
    """Service for Workflow business logic"""
    
    def __init__(self, repository: WorkflowRepository, 
                 llm_service=None, 
                 mcp_service=None, 
                 rag_service=None,
                 rest_api_service=None):
        super().__init__(repository)
        self.llm_service = llm_service
        self.mcp_service = mcp_service
        self.rag_service = rag_service
        self.rest_api_service = rest_api_service
    
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
    
    def get_node_options(self, organization_id: UUID) -> Dict[str, Any]:
        """Get available node options from organization resources via services"""
        options = {
            "llms": [],
            "mcp_tools": [],
            "rag_connectors": [],
            "rest_apis": []
        }
        
        try:
            # Get LLMs for this organization via LLM service
            if self.llm_service:
                llms = self.llm_service.list_llms(str(organization_id))
                options["llms"] = [
                    {
                        "id": llm["id"],
                        "name": llm["name"],
                        "description": llm.get("description", ""),
                        "model_name": llm["model_name"],
                        "provider": llm.get("custom_llm_provider", "Unknown"),
                        "status": llm["status"],
                        "enabled": llm["enabled"]
                    }
                    for llm in llms if llm["enabled"] and llm["status"] == "active"
                ]
            
            # Get MCP Tools for this organization via MCP service
            if self.mcp_service:
                mcp_tools = self.mcp_service.list_tools(str(organization_id))
                options["mcp_tools"] = [
                    {
                        "id": tool["id"],
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "tool_type": tool.get("tool_type", ""),
                        "status": tool.get("status", "active"),
                        "enabled": tool["enabled"]
                    }
                    for tool in mcp_tools if tool["enabled"]
                ]
            
            # Get RAG Connectors for this organization via RAG service
            if self.rag_service:
                rag_connectors = self.rag_service.list_connectors(str(organization_id))
                options["rag_connectors"] = [
                    {
                        "id": connector["id"],
                        "name": connector["name"],
                        "description": connector.get("description", ""),
                        "connector_type": connector.get("connector_type", ""),
                        "status": connector.get("status", "active"),
                        "enabled": connector["enabled"]
                    }
                    for connector in rag_connectors if connector["enabled"]
                ]
            
            # Get REST APIs for this organization via REST API service
            if self.rest_api_service:
                rest_apis = self.rest_api_service.list_apis(str(organization_id))
                options["rest_apis"] = [
                    {
                        "id": api["id"],
                        "name": api["name"],
                        "description": api.get("description", ""),
                        "method": api["method"],
                        "base_url": api["base_url"],
                        "resource_path": api.get("resource_path", ""),
                        "tags": api.get("tags", []),
                        "status": api.get("status", "active"),
                        "enabled": api["enabled"]
                    }
                    for api in rest_apis if api["enabled"] and api.get("status") == "active"
                ]
            
            self.logger.info(f"Retrieved node options for organization {organization_id}: "
                           f"{len(options['llms'])} LLMs, {len(options['mcp_tools'])} MCP tools, "
                           f"{len(options['rag_connectors'])} RAG connectors, "
                           f"{len(options['rest_apis'])} REST APIs")
            
            return options
            
        except Exception as e:
            self.logger.error(f"Error getting node options for organization {organization_id}: {e}")
            raise
    