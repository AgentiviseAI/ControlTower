"""
REST API Service implementation
"""
import json
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from app.repositories import RestAPIRepository
from app.repositories.intent_data_repository import IntentDataRepository
from app.core.exceptions import NotFoundError, ConflictError, ValidationException
from .base import BaseService


class RestAPIService(BaseService):
    """Service for REST API business logic"""
    
    def __init__(self, repository: RestAPIRepository, intent_data_repository: Optional[IntentDataRepository] = None):
        super().__init__(repository)
        self.intent_data_repository = intent_data_repository
    
    def _create_intent_data_for_api(self, organization_id: str, api_id: str, api_name: str, api_description: str = None):
        """Helper method to create intent data for REST API"""
        if self.intent_data_repository:
            try:
                intent_data = self.intent_data_repository.create(
                    organization_id=organization_id,
                    name=f"API: {api_name}",
                    description=api_description or f"Intent data for REST API: {api_name}",
                    source_type="rest_api",
                    source_id=api_id,
                    category="API",
                    enabled=True
                )
                self.logger.info(f"Created intent data for REST API: {api_name}")
            except Exception as e:
                self.logger.error(f"Failed to create intent data for REST API {api_name}: {e}")
    
    def _update_intent_data_for_api(self, organization_id: str, api_id: str, api_name: str, api_description: str = None):
        """Helper method to update intent data for REST API"""
        if self.intent_data_repository:
            try:
                # Find existing intent data for this REST API
                intent_data_list = self.intent_data_repository.list_by_source_type(organization_id, "rest_api")
                for intent_data in intent_data_list:
                    if intent_data.source_id == api_id:
                        intent_data.name = f"API: {api_name}"
                        intent_data.description = api_description or f"Intent data for REST API: {api_name}"
                        self.intent_data_repository.update(intent_data)
                        self.logger.info(f"Updated intent data for REST API: {api_name}")
                        break
            except Exception as e:
                self.logger.error(f"Failed to update intent data for REST API {api_name}: {e}")
    
    def _delete_intent_data_for_api(self, organization_id: str, api_id: str):
        """Helper method to delete intent data for REST API"""
        if self.intent_data_repository:
            try:
                deleted_count = self.intent_data_repository.delete_by_source(organization_id, "rest_api", api_id)
                if deleted_count > 0:
                    self.logger.info(f"Deleted {deleted_count} intent data records for REST API: {api_id}")
            except Exception as e:
                self.logger.error(f"Failed to delete intent data for REST API {api_id}: {e}")
    
    def create_api(self, organization_id: str, name: str, base_url: str, method: str = "GET",
                   description: str = None, version: str = "v1", resource_path: str = None,
                   request_schema: Dict[str, Any] = None, response_schema: Dict[str, Any] = None,
                   headers: Dict[str, str] = None, auth_headers: Dict[str, str] = None,
                   cookies: Dict[str, str] = None, query_params: Dict[str, Any] = None,
                   path_params: Dict[str, Any] = None, tags: List[str] = None,
                   auth_method: str = None, enabled: bool = True,
                   openapi_spec_url: str = None, operation_id: str = None,
                   rate_limit: Dict[str, Any] = None, timeout: Dict[str, int] = None,
                   documentation_url: str = None, examples: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new REST API configuration"""
        self._validate_data({'name': name, 'base_url': base_url, 'method': method}, 
                          ['name', 'base_url', 'method'])
        
        # Validate HTTP method
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method.upper() not in valid_methods:
            raise ValidationException(f"Invalid HTTP method. Must be one of: {', '.join(valid_methods)}")
        
        # Check if REST API with same name exists in this organization
        existing_api = self.repository.get_by_name_and_organization(name, organization_id)
        if existing_api:
            raise ConflictError(f"REST API with name '{name}' already exists in this organization")
        
        self.logger.info(f"Creating REST API: {name} ({method} {base_url}) for organization: {organization_id}")
        
        # Set defaults
        timeout = timeout or {"connect": 30, "read": 60}
        
        api = self.repository.create(
            name=name,
            description=description,
            base_url=base_url,
            version=version,
            method=method.upper(),
            resource_path=resource_path,
            request_schema=request_schema,
            response_schema=response_schema,
            headers=headers or {},
            auth_headers=auth_headers or {},
            cookies=cookies or {},
            query_params=query_params or {},
            path_params=path_params or {},
            openapi_spec_url=openapi_spec_url,
            operation_id=operation_id,
            tags=tags or [],
            organization_id=organization_id,
            auth_method=auth_method,
            enabled=enabled,
            status="active",
            rate_limit=rate_limit,
            timeout=timeout,
            documentation_url=documentation_url,
            examples=examples or {}
        )
        
        # Create intent data for the new REST API
        self._create_intent_data_for_api(organization_id, str(api.id), name, description)
        
        return self._to_dict(api)
    
    def create_multiple_apis(self, organization_id: str, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple REST API configurations"""
        created_apis = []
        
        for api_data in apis:
            try:
                # Add organization_id to each API data
                api_data['organization_id'] = organization_id
                api = self.create_api(**api_data)
                created_apis.append(api)
            except Exception as e:
                self.logger.error(f"Failed to create API {api_data.get('name', 'Unknown')}: {e}")
                # Continue with other APIs, but log the error
                created_apis.append({
                    "name": api_data.get('name', 'Unknown'),
                    "error": str(e),
                    "status": "failed"
                })
        
        return created_apis
    
    async def create_from_openapi_spec(self, organization_id: str, spec_url: str, 
                                     tags_to_attach: List[str] = None) -> List[Dict[str, Any]]:
        """Create multiple REST APIs from OpenAPI/Swagger specification"""
        try:
            # Download the OpenAPI specification
            async with aiohttp.ClientSession() as session:
                async with session.get(spec_url) as response:
                    if response.status != 200:
                        raise ValidationException(f"Failed to fetch OpenAPI spec: HTTP {response.status}")
                    
                    spec_content = await response.text()
                    openapi_spec = json.loads(spec_content)
            
            # Parse the OpenAPI specification and create API configurations
            apis = self._parse_openapi_spec(openapi_spec, spec_url, tags_to_attach)
            
            # Create the APIs
            created_apis = []
            for api_data in apis:
                api_data['organization_id'] = organization_id
                try:
                    api = self.create_api(**api_data)
                    created_apis.append(api)
                except Exception as e:
                    self.logger.error(f"Failed to create API from OpenAPI spec: {e}")
                    created_apis.append({
                        "name": api_data.get('name', 'Unknown'),
                        "error": str(e),
                        "status": "failed"
                    })
            
            return created_apis
            
        except Exception as e:
            raise ValidationException(f"Failed to process OpenAPI specification: {e}")
    
    def _parse_openapi_spec(self, spec: Dict[str, Any], spec_url: str, 
                           tags_to_attach: List[str] = None) -> List[Dict[str, Any]]:
        """Parse OpenAPI specification and extract API configurations"""
        apis = []
        
        base_url = self._extract_base_url(spec)
        paths = spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    continue
                
                # Get operation tags from OpenAPI spec
                operation_tags = operation.get('tags', [])
                
                # Combine operation tags with user-provided tags for better organization
                final_tags = operation_tags.copy()
                if tags_to_attach:
                    final_tags.extend(tags_to_attach)
                
                # Remove duplicates while preserving order
                final_tags = list(dict.fromkeys(final_tags))
                
                # Extract API information
                api_config = {
                    'name': operation.get('operationId') or f"{method.upper()} {path}",
                    'description': operation.get('summary') or operation.get('description'),
                    'base_url': base_url,
                    'method': method.upper(),
                    'resource_path': path,
                    'operation_id': operation.get('operationId'),
                    'tags': final_tags,
                    'openapi_spec_url': spec_url,
                    'request_schema': self._extract_request_schema(operation),
                    'response_schema': self._extract_response_schema(operation),
                    'path_params': self._extract_path_params(operation),
                    'query_params': self._extract_query_params(operation),
                    'headers': self._extract_headers(operation),
                    'examples': self._extract_examples(operation)
                }
                
                apis.append(api_config)
        
        return apis
    
    def _extract_base_url(self, spec: Dict[str, Any]) -> str:
        """Extract base URL from OpenAPI spec"""
        # OpenAPI 3.0
        if 'servers' in spec and spec['servers']:
            return spec['servers'][0]['url']
        
        # OpenAPI 2.0 (Swagger)
        if 'host' in spec:
            scheme = spec.get('schemes', ['https'])[0]
            host = spec['host']
            base_path = spec.get('basePath', '')
            return f"{scheme}://{host}{base_path}"
        
        return "https://api.example.com"
    
    def _extract_request_schema(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract request schema from operation"""
        request_body = operation.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            json_content = content.get('application/json', {})
            return json_content.get('schema')
        return None
    
    def _extract_response_schema(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract response schema from operation"""
        responses = operation.get('responses', {})
        success_response = responses.get('200') or responses.get('201')
        if success_response:
            content = success_response.get('content', {})
            json_content = content.get('application/json', {})
            return json_content.get('schema')
        return None
    
    def _extract_path_params(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract path parameters from operation"""
        parameters = operation.get('parameters', [])
        path_params = {}
        
        for param in parameters:
            if param.get('in') == 'path':
                path_params[param['name']] = {
                    'type': param.get('schema', {}).get('type', 'string'),
                    'description': param.get('description'),
                    'required': param.get('required', True)
                }
        
        return path_params
    
    def _extract_query_params(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract query parameters from operation"""
        parameters = operation.get('parameters', [])
        query_params = {}
        
        for param in parameters:
            if param.get('in') == 'query':
                query_params[param['name']] = {
                    'type': param.get('schema', {}).get('type', 'string'),
                    'description': param.get('description'),
                    'required': param.get('required', False),
                    'default': param.get('schema', {}).get('default')
                }
        
        return query_params
    
    def _extract_headers(self, operation: Dict[str, Any]) -> Dict[str, str]:
        """Extract headers from operation"""
        parameters = operation.get('parameters', [])
        headers = {}
        
        for param in parameters:
            if param.get('in') == 'header':
                headers[param['name']] = param.get('description', '')
        
        return headers
    
    def _extract_examples(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract examples from operation"""
        examples = {}
        
        # Request examples
        request_body = operation.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            for media_type, media_content in content.items():
                if 'example' in media_content:
                    examples[f'request_{media_type}'] = media_content['example']
        
        # Response examples
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            content = response.get('content', {})
            for media_type, media_content in content.items():
                if 'example' in media_content:
                    examples[f'response_{status_code}_{media_type}'] = media_content['example']
        
        return examples
    
    def get_api(self, api_id: str) -> Optional[Dict[str, Any]]:
        """Get REST API by ID"""
        api = self.repository.get_by_id(api_id)
        if not api:
            raise NotFoundError("REST API", api_id)
        return self._to_dict(api)
    
    def get_all_apis(self) -> List[Dict[str, Any]]:
        """Get all REST APIs"""
        apis = self.repository.get_all()
        return [self._to_dict(api) for api in apis]
    
    def list_apis(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all REST APIs for a specific organization"""
        apis = self.repository.get_by_organization(organization_id)
        return [self._to_dict(api) for api in apis]
    
    def list_apis_by_tags(self, organization_id: str, tags: List[str]) -> List[Dict[str, Any]]:
        """Get REST APIs by tags for a specific organization"""
        apis = self.repository.get_by_tags(organization_id, tags)
        return [self._to_dict(api) for api in apis]
    
    def update_api(self, api_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update REST API"""
        self.logger.info(f"Updating REST API: {api_id}")
        
        # Validate HTTP method if provided
        if 'method' in kwargs:
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
            if kwargs['method'].upper() not in valid_methods:
                raise ValidationException(f"Invalid HTTP method. Must be one of: {', '.join(valid_methods)}")
            kwargs['method'] = kwargs['method'].upper()
        
        api = self.repository.update(api_id, **kwargs)
        if not api:
            raise NotFoundError("REST API", api_id)
        
        # Update intent data if name or description changed
        if 'name' in kwargs or 'description' in kwargs:
            self._update_intent_data_for_api(api.organization_id, api_id, api.name, api.description)
        
        return self._to_dict(api)
    
    def delete_api(self, api_id: str) -> bool:
        """Delete REST API"""
        self.logger.info(f"Deleting REST API: {api_id}")
        
        # Get the API first to retrieve organization_id
        api = self.repository.get_by_id(api_id)
        if not api:
            raise NotFoundError("REST API", api_id)
        
        organization_id = api.organization_id
        
        success = self.repository.delete(api_id)
        if not success:
            raise NotFoundError("REST API", api_id)
        
        # Delete associated intent data
        self._delete_intent_data_for_api(organization_id, api_id)
        
        return success
    
    def delete_multiple_apis(self, api_ids: List[str]) -> Dict[str, Any]:
        """Delete multiple REST APIs"""
        results = {
            "deleted": [],
            "failed": [],
            "not_found": []
        }
        
        for api_id in api_ids:
            try:
                if self.delete_api(api_id):
                    results["deleted"].append(api_id)
                else:
                    results["failed"].append(api_id)
            except NotFoundError:
                results["not_found"].append(api_id)
            except Exception as e:
                self.logger.error(f"Failed to delete API {api_id}: {e}")
                results["failed"].append(api_id)
        
        return results
