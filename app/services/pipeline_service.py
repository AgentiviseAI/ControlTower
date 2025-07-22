"""
Pipeline Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import PipelineRepository
from app.core.exceptions import NotFoundError
from .base import BaseService


class PipelineService(BaseService):
    """Service for Pipeline business logic"""
    
    def __init__(self, repository: PipelineRepository):
        super().__init__(repository)
    
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
    
    def _create_default_pipeline(self) -> Dict[str, Any]:
        """Create a default pipeline structure"""
        return {
            "id": "default-pipeline",
            "name": "Default Pipeline",
            "description": "Default pipeline configuration",
            "nodes": [
                {
                    "id": "input-node",
                    "type": "input",
                    "position": {"x": 100, "y": 100},
                    "config": {"input_type": "text"}
                },
                {
                    "id": "process-node", 
                    "type": "llm",
                    "position": {"x": 300, "y": 100},
                    "config": {"model": "default"}
                },
                {
                    "id": "output-node",
                    "type": "output", 
                    "position": {"x": 500, "y": 100},
                    "config": {"output_type": "text"}
                }
            ],
            "edges": [
                {
                    "source_component_id": "input-node",
                    "target_component_id": "process-node"
                },
                {
                    "source_component_id": "process-node",
                    "target_component_id": "output-node"
                }
            ],
            "status": "draft"
        }
