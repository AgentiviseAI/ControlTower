"""
LLM Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import LLMRepository
from app.core.exceptions import NotFoundError
from .base import BaseService


class LLMService(BaseService):
    """Service for LLM business logic"""
    
    def __init__(self, repository: LLMRepository):
        super().__init__(repository)
    
    def create_llm(self, name: str, model_name: str, provider: str, enabled: bool = True,
                  endpoint_url: str = None, status: str = "active",
                  usage_stats: Dict[str, Any] = None, 
                  config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new LLM"""
        self._validate_data({
            'name': name, 'model_name': model_name, 
            'provider': provider, 'endpoint_url': endpoint_url
        }, ['name', 'model_name', 'provider', 'endpoint_url'])
        
        self.logger.info(f"Creating LLM: {name}")
        
        llm = self.repository.create(
            name=name,
            model_name=model_name,
            provider=provider,
            enabled=enabled,
            endpoint_url=endpoint_url,
            status=status,
            usage_stats=usage_stats or {},
            config=config or {}
        )
        
        return self._to_dict(llm)
    
    def get_llm(self, llm_id: str) -> Optional[Dict[str, Any]]:
        """Get LLM by ID"""
        llm = self.repository.get_by_id(llm_id)
        if not llm:
            raise NotFoundError("LLM", llm_id)
        return self._to_dict(llm)
    
    def get_all_llms(self) -> List[Dict[str, Any]]:
        """Get all LLMs"""
        llms = self.repository.get_all()
        return [self._to_dict(llm) for llm in llms]
    
    def update_llm(self, llm_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update LLM"""
        self.logger.info(f"Updating LLM: {llm_id}")
        
        llm = self.repository.update(llm_id, **kwargs)
        if not llm:
            raise NotFoundError("LLM", llm_id)
        
        return self._to_dict(llm)
    
    def delete_llm(self, llm_id: str) -> bool:
        """Delete LLM"""
        self.logger.info(f"Deleting LLM: {llm_id}")
        
        success = self.repository.delete(llm_id)
        if not success:
            raise NotFoundError("LLM", llm_id)
        
        return success
