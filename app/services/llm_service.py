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
    
    def create_llm(self, name: str, model_name: str, hosting_environment: str, 
                  enabled: bool = True, status: str = "active",
                  description: str = None, usage_stats: Dict[str, Any] = None,
                  # Model parameters
                  temperature: float = None, max_tokens: int = None, 
                  top_p: float = None, top_k: int = None,
                  frequency_penalty: float = None, presence_penalty: float = None,
                  stop_sequences: str = None,
                  # Azure AI Foundry fields
                  azure_endpoint_url: str = None, azure_api_key: str = None,
                  azure_deployment_name: str = None,
                  # AWS Bedrock fields
                  aws_region: str = None, aws_access_key_id: str = None,
                  aws_secret_access_key: str = None, aws_model_id: str = None,
                  # AWS SageMaker fields
                  aws_sagemaker_endpoint_name: str = None, aws_content_handler_class: str = None,
                  # Google Cloud Vertex AI fields
                  gcp_project_id: str = None, gcp_region: str = None,
                  gcp_auth_method: str = None, gcp_service_account_key: str = None,
                  gcp_api_key: str = None, gcp_model_type: str = None,
                  gcp_model_name: str = None,
                  # Custom Deployment fields
                  custom_deployment_location: str = None, custom_llm_provider: str = None,
                  custom_api_endpoint_url: str = None, custom_api_compatibility: str = None,
                  custom_auth_method: str = None, custom_auth_header_name: str = None,
                  custom_auth_key_prefix: str = None, custom_auth_api_key: str = None,
                  custom_auth_username: str = None, custom_auth_password: str = None,
                  custom_oauth2_token_url: str = None, custom_oauth2_client_id: str = None,
                  custom_oauth2_client_secret: str = None,
                  **kwargs) -> Dict[str, Any]:
        """Create a new LLM with comprehensive deployment configuration"""
        self._validate_data({
            'name': name, 'model_name': model_name, 'hosting_environment': hosting_environment
        }, ['name', 'model_name', 'hosting_environment'])
        
        self.logger.info(f"Creating LLM: {name} with hosting environment: {hosting_environment}")
        
        # Prepare all the data for the repository
        llm_data = {
            'name': name,
            'model_name': model_name,
            'hosting_environment': hosting_environment,
            'enabled': enabled,
            'status': status,
            'description': description,
            'usage_stats': usage_stats or {},
            # Model parameters
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_p': top_p,
            'top_k': top_k,
            'frequency_penalty': frequency_penalty,
            'presence_penalty': presence_penalty,
            'stop_sequences': stop_sequences,
            # Azure AI Foundry fields
            'azure_endpoint_url': azure_endpoint_url,
            'azure_api_key': azure_api_key,
            'azure_deployment_name': azure_deployment_name,
            # AWS Bedrock fields
            'aws_region': aws_region,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'aws_model_id': aws_model_id,
            # AWS SageMaker fields
            'aws_sagemaker_endpoint_name': aws_sagemaker_endpoint_name,
            'aws_content_handler_class': aws_content_handler_class,
            # Google Cloud Vertex AI fields
            'gcp_project_id': gcp_project_id,
            'gcp_region': gcp_region,
            'gcp_auth_method': gcp_auth_method,
            'gcp_service_account_key': gcp_service_account_key,
            'gcp_api_key': gcp_api_key,
            'gcp_model_type': gcp_model_type,
            'gcp_model_name': gcp_model_name,
            # Custom Deployment fields
            'custom_deployment_location': custom_deployment_location,
            'custom_llm_provider': custom_llm_provider,
            'custom_api_endpoint_url': custom_api_endpoint_url,
            'custom_api_compatibility': custom_api_compatibility,
            'custom_auth_method': custom_auth_method,
            'custom_auth_header_name': custom_auth_header_name,
            'custom_auth_key_prefix': custom_auth_key_prefix,
            'custom_auth_api_key': custom_auth_api_key,
            'custom_auth_username': custom_auth_username,
            'custom_auth_password': custom_auth_password,
            'custom_oauth2_token_url': custom_oauth2_token_url,
            'custom_oauth2_client_id': custom_oauth2_client_id,
            'custom_oauth2_client_secret': custom_oauth2_client_secret,
        }
        
        # Add any additional kwargs
        llm_data.update(kwargs)
        
        # Remove None values to avoid issues
        llm_data = {k: v for k, v in llm_data.items() if v is not None}
        
        # Validate hosting environment configuration
        self._validate_hosting_environment_config(hosting_environment, llm_data)
        
        llm = self.repository.create(**llm_data)
        
        return self._to_dict(llm)
    
    def _validate_hosting_environment_config(self, hosting_environment: str, data: Dict[str, Any]) -> None:
        """Validate that required fields for the hosting environment are provided"""
        if hosting_environment == 'azure_ai_foundry':
            required_fields = ['azure_endpoint_url', 'azure_api_key', 'azure_deployment_name']
        elif hosting_environment == 'aws_bedrock':
            required_fields = ['aws_region', 'aws_access_key_id', 'aws_secret_access_key', 'aws_model_id']
        elif hosting_environment == 'aws_sagemaker':
            required_fields = ['aws_region', 'aws_access_key_id', 'aws_secret_access_key', 'aws_sagemaker_endpoint_name']
        elif hosting_environment == 'gcp_vertex_ai':
            required_fields = ['gcp_project_id', 'gcp_region', 'gcp_auth_method']
        elif hosting_environment == 'custom_deployment':
            required_fields = ['custom_api_endpoint_url', 'custom_api_compatibility', 'custom_auth_method']
            # Validate that custom API compatibility is supported
            if data.get('custom_api_compatibility') == 'custom':
                raise ValueError("Custom API compatibility is not supported yet. Please choose 'openai_compatible', 'anthropic_compatible', 'hf_tgi_compatible', or 'ollama_compatible'.")
        else:
            raise ValueError(f"Unknown hosting environment: {hosting_environment}")
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields for {hosting_environment}: {missing_fields}")
    
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
        """Update LLM with new deployment configuration support"""
        self.logger.info(f"Updating LLM: {llm_id}")
        
        # If hosting_environment is being updated, validate the configuration
        if 'hosting_environment' in kwargs:
            self._validate_hosting_environment_config(kwargs['hosting_environment'], kwargs)
        
        # Remove None values to avoid issues
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        llm = self.repository.update(llm_id, **update_data)
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
    
    def get_llms_by_hosting_environment(self, hosting_environment: str) -> List[Dict[str, Any]]:
        """Get all LLMs for a specific hosting environment"""
        all_llms = self.get_all_llms()
        return [llm for llm in all_llms if llm.get('hosting_environment') == hosting_environment]
    
    def get_active_llms(self) -> List[Dict[str, Any]]:
        """Get all active and enabled LLMs"""
        all_llms = self.get_all_llms()
        return [llm for llm in all_llms if llm.get('enabled') and llm.get('status') == 'active']
    
    def update_usage_stats(self, llm_id: str, requests_today: int = None, 
                          tokens_used: int = None, rate_limit: int = None) -> Dict[str, Any]:
        """Update usage statistics for an LLM"""
        llm = self.get_llm(llm_id)
        current_stats = llm.get('usage_stats', {})
        
        if requests_today is not None:
            current_stats['requests_today'] = requests_today
        if tokens_used is not None:
            current_stats['tokens_used'] = tokens_used
        if rate_limit is not None:
            current_stats['rate_limit'] = rate_limit
            
        return self.update_llm(llm_id, usage_stats=current_stats)
