"""
Pipeline Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import PipelineRepository, LLMRepository, MCPToolRepository, RAGConnectorRepository
from app.core.exceptions import NotFoundError
from .base import BaseService


class PipelineService(BaseService):
    """Service for Pipeline business logic"""
    
    def __init__(self, repository: PipelineRepository, 
                 llm_repository: LLMRepository = None, 
                 mcp_repository: MCPToolRepository = None, 
                 rag_repository: RAGConnectorRepository = None):
        super().__init__(repository)
        self.llm_repository = llm_repository
        self.mcp_repository = mcp_repository
        self.rag_repository = rag_repository
    
    def create_pipeline(self, name: str, description: str = None, 
                       nodes: List[Dict[str, Any]] = None, 
                       edges: List[Dict[str, Any]] = None,
                       status: str = "draft") -> Dict[str, Any]:
        """Create a new pipeline"""
        self._validate_data({'name': name}, ['name'])
        
        self.logger.info(f"Creating pipeline: {name}")
        
        pipeline = self.repository.create(
            name=name,
            description=description,
            nodes=nodes or [],
            edges=edges or [],
            status=status
        )
        
        return self._pipeline_to_dict(pipeline)
    
    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline by ID"""
        pipeline = self.repository.get_by_id(pipeline_id)
        if not pipeline:
            raise NotFoundError("Pipeline", pipeline_id)
        return self._pipeline_to_dict(pipeline)
    
    def get_all_pipelines(self) -> List[Dict[str, Any]]:
        """Get all pipelines"""
        pipelines = self.repository.get_all()
        return [self._pipeline_to_dict(pipeline) for pipeline in pipelines]
    
    def update_pipeline(self, pipeline_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update pipeline"""
        self.logger.info(f"Updating pipeline: {pipeline_id}")
        
        pipeline = self.repository.update(pipeline_id, **kwargs)
        if not pipeline:
            raise NotFoundError("Pipeline", pipeline_id)
        
        return self._pipeline_to_dict(pipeline)
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete pipeline"""
        self.logger.info(f"Deleting pipeline: {pipeline_id}")
        
        success = self.repository.delete(pipeline_id)
        if not success:
            raise NotFoundError("Pipeline", pipeline_id)
        
        return success
    
    def get_node_options(self) -> Dict[str, Any]:
        """Get available options for pipeline nodes"""
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
    
    def _pipeline_to_dict(self, pipeline) -> Dict[str, Any]:
        """Convert pipeline to dict with proper node handling"""
        if not pipeline:
            return None
        
        result = self._to_dict(pipeline)
        # Ensure nodes are properly formatted
        if 'nodes' in result and result['nodes']:
            # Convert components to nodes format for compatibility
            result['nodes'] = result['nodes']
        
        return result
    
    def create_default_pipeline(self, agent_name: str) -> Dict[str, Any]:
        """Create a default pipeline for an agent with proper LLM linking"""
        import uuid
        
        # Generate UUIDs for nodes
        start_node_id = str(uuid.uuid4())
        end_node_id = str(uuid.uuid4())
        
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
        
        # Create pipeline based on whether Gemma LLM exists
        if gemma_llm_id:
            # Create 3-node pipeline: start -> llm -> end
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
            self.logger.info(f"Creating default pipeline with 'Gemma 2 2B (Self-hosted)' LLM linked")
        else:
            # Create 2-node pipeline: start -> end (no LLM available)
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
            self.logger.info(f"Creating simple start->end pipeline (no 'Gemma 2 2B (Self-hosted)' LLM found)")
        
        # Create the pipeline
        return self.create_pipeline(
            name=f"{agent_name} - Default Pipeline",
            description=f"Default pipeline for agent {agent_name}",
            nodes=nodes,
            edges=edges,
            status="draft"
        )
