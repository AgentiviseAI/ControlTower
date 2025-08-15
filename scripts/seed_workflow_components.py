"""
Seed workflow component definitions
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.workflow_component_definition import WorkflowComponentDefinition
from app.core.database import get_database_url

# Database setup
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Component definitions based on the existing frontend components
COMPONENT_DEFINITIONS = [
    {
        'component_id': 'llm',
        'name': 'LLM Model',
        'category': 'AI Models',
        'description': 'Large Language Model processing node',
        'icon_name': 'ThunderboltOutlined',
        'color': '#1890ff',
        'sort_order': 1,
        'config_schema': {
            'type': 'object',
            'properties': {
                'link': {
                    'type': 'string',
                    'title': 'LLM Selection',
                    'description': 'Select the LLM to use'
                },
                'temperature': {
                    'type': 'number',
                    'title': 'Temperature',
                    'description': 'Sampling temperature',
                    'minimum': 0.0,
                    'maximum': 2.0,
                    'default': 0.7
                },
                'max_tokens': {
                    'type': 'integer',
                    'title': 'Max Tokens',
                    'description': 'Maximum tokens to generate',
                    'minimum': 1,
                    'maximum': 4096,
                    'default': 1000
                },
                'top_p': {
                    'type': 'number',
                    'title': 'Top P',
                    'description': 'Nucleus sampling parameter',
                    'minimum': 0.0,
                    'maximum': 1.0,
                    'default': 1.0
                }
            },
            'required': ['link']
        },
        'default_config': {
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 1.0
        },
        'input_ports': [
            {'name': 'prompt', 'type': 'string', 'description': 'Input prompt', 'required': True}
        ],
        'output_ports': [
            {'name': 'response', 'type': 'string', 'description': 'LLM response', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.llm_prompt_node.LLMPromptNode',
        'tags': ['ai', 'llm', 'generation']
    },
    {
        'component_id': 'intent_extractor',
        'name': 'Intent Extractor',
        'category': 'AI Models',
        'description': 'Extract user intents using LLM with customizable system prompts',
        'icon_name': 'EyeOutlined',
        'color': '#722ed1',
        'sort_order': 2,
        'config_schema': {
            'type': 'object',
            'properties': {
                'link': {
                    'type': 'string',
                    'title': 'LLM Selection',
                    'description': 'Select the LLM to use for intent extraction'
                },
                'system_prompt': {
                    'type': 'string',
                    'title': 'Custom System Prompt',
                    'description': 'Optional custom instructions to add to the default system prompt',
                    'format': 'textarea'
                },
                'temperature': {
                    'type': 'number',
                    'title': 'Temperature',
                    'description': 'Sampling temperature (lower values for more focused extraction)',
                    'minimum': 0.0,
                    'maximum': 2.0,
                    'default': 0.3
                },
                'max_tokens': {
                    'type': 'integer',
                    'title': 'Max Tokens',
                    'description': 'Maximum tokens to generate',
                    'minimum': 1,
                    'maximum': 2048,
                    'default': 500
                },
                'top_p': {
                    'type': 'number',
                    'title': 'Top P',
                    'description': 'Nucleus sampling parameter',
                    'minimum': 0.0,
                    'maximum': 1.0,
                    'default': 1.0
                }
            },
            'required': ['link']
        },
        'default_config': {
            'temperature': 0.3,
            'max_tokens': 500,
            'top_p': 1.0
        },
        'input_ports': [
            {'name': 'user_input', 'type': 'string', 'description': 'User input to analyze for intent', 'required': True}
        ],
        'output_ports': [
            {'name': 'extracted_intent', 'type': 'string', 'description': 'Extracted intent analysis', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.intent_extractor_node.IntentExtractorNode',
        'tags': ['ai', 'llm', 'intent', 'extraction', 'analysis']
    },
    {
        'component_id': 'knowledgebase_retriever',
        'name': 'Knowledgebase Retriever',
        'category': 'AI Models',
        'description': 'Knowledge retrieval with search type options',
        'icon_name': 'DatabaseOutlined',
        'color': '#52c41a',
        'sort_order': 3,
        'config_schema': {
            'type': 'object',
            'properties': {
                'link': {
                    'type': 'string',
                    'title': 'Knowledge Base',
                    'description': 'Select the knowledge base to query'
                },
                'max_results': {
                    'type': 'integer',
                    'title': 'Max Results',
                    'description': 'Maximum number of results to return',
                    'minimum': 1,
                    'maximum': 100,
                    'default': 10
                },
                'similarity_threshold': {
                    'type': 'number',
                    'title': 'Similarity Threshold',
                    'description': 'Minimum similarity score',
                    'minimum': 0.0,
                    'maximum': 1.0,
                    'default': 0.8
                },
                'filters': {
                    'type': 'object',
                    'title': 'Filters',
                    'description': 'Additional search filters',
                    'default': {}
                }
            },
            'required': ['link']
        },
        'default_config': {
            'max_results': 10,
            'similarity_threshold': 0.8,
            'filters': {}
        },
        'input_ports': [
            {'name': 'query', 'type': 'string', 'description': 'Search query', 'required': True}
        ],
        'output_ports': [
            {'name': 'results', 'type': 'array', 'description': 'Retrieved documents', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.rag_retriever_node.RAGRetrieverNode',
        'tags': ['rag', 'knowledge', 'retrieval']
    },
    {
        'component_id': 'prompt_rewriter',
        'name': 'Prompt Rewriter',
        'category': 'Processing',
        'description': 'Rewrites and optimizes prompts for better results',
        'icon_name': 'EditOutlined',
        'color': '#ff7a45',
        'sort_order': 1,
        'config_schema': {
            'type': 'object',
            'properties': {
                'rewrite_strategy': {
                    'type': 'string',
                    'title': 'Rewrite Strategy',
                    'description': 'How to rewrite the prompt',
                    'enum': ['enhance', 'simplify', 'formalize', 'contextualize'],
                    'default': 'enhance'
                },
                'preserve_intent': {
                    'type': 'boolean',
                    'title': 'Preserve Intent',
                    'description': 'Maintain original prompt intent',
                    'default': True
                }
            }
        },
        'default_config': {
            'rewrite_strategy': 'enhance',
            'preserve_intent': True
        },
        'input_ports': [
            {'name': 'prompt', 'type': 'string', 'description': 'Original prompt', 'required': True}
        ],
        'output_ports': [
            {'name': 'rewritten_prompt', 'type': 'string', 'description': 'Optimized prompt', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.prompt_rewriter_node.PromptRewriterNode',
        'tags': ['prompt', 'processing', 'optimization']
    },
    {
        'component_id': 'inject_context',
        'name': 'Inject Conversation Context',
        'category': 'Processing',
        'description': 'Injects conversation history and context',
        'icon_name': 'MessageOutlined',
        'color': '#40a9ff',
        'sort_order': 2,
        'config_schema': {
            'type': 'object',
            'properties': {
                'max_history_length': {
                    'type': 'integer',
                    'title': 'Max History Length',
                    'description': 'Maximum number of previous messages to include',
                    'minimum': 1,
                    'maximum': 50,
                    'default': 10
                },
                'include_system_messages': {
                    'type': 'boolean',
                    'title': 'Include System Messages',
                    'description': 'Include system messages in context',
                    'default': False
                }
            }
        },
        'default_config': {
            'max_history_length': 10,
            'include_system_messages': False
        },
        'input_ports': [
            {'name': 'prompt', 'type': 'string', 'description': 'Current prompt', 'required': True},
            {'name': 'context', 'type': 'array', 'description': 'Conversation history', 'required': False}
        ],
        'output_ports': [
            {'name': 'contextualized_prompt', 'type': 'string', 'description': 'Prompt with context', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.context_injector_node.ContextInjectorNode',
        'tags': ['context', 'conversation', 'processing']
    },
    {
        'component_id': 'mcp_tool_selector',
        'name': 'MCP Tool Selector',
        'category': 'Tools',
        'description': 'Selects appropriate MCP tools based on context',
        'icon_name': 'ToolOutlined',
        'color': '#722ed1',
        'sort_order': 1,
        'config_schema': {
            'type': 'object',
            'properties': {
                'selection_strategy': {
                    'type': 'string',
                    'title': 'Selection Strategy',
                    'description': 'How to select tools',
                    'enum': ['best_match', 'multiple', 'weighted'],
                    'default': 'best_match'
                },
                'max_tools': {
                    'type': 'integer',
                    'title': 'Max Tools',
                    'description': 'Maximum number of tools to select',
                    'minimum': 1,
                    'maximum': 10,
                    'default': 3
                }
            }
        },
        'default_config': {
            'selection_strategy': 'best_match',
            'max_tools': 3
        },
        'input_ports': [
            {'name': 'query', 'type': 'string', 'description': 'Tool selection query', 'required': True}
        ],
        'output_ports': [
            {'name': 'selected_tools', 'type': 'array', 'description': 'Selected MCP tools', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.mcp_tool_selector_node.MCPToolSelectorNode',
        'tags': ['mcp', 'tool', 'selection']
    },
    {
        'component_id': 'mcp_tool_orchestrator',
        'name': 'MCP Tool Orchestrator',
        'category': 'Tools',
        'description': 'Orchestrates multiple MCP tool executions',
        'icon_name': 'ControlOutlined',
        'color': '#9254de',
        'sort_order': 2,
        'config_schema': {
            'type': 'object',
            'properties': {
                'execution_mode': {
                    'type': 'string',
                    'title': 'Execution Mode',
                    'description': 'How to execute multiple tools',
                    'enum': ['sequential', 'parallel', 'conditional'],
                    'default': 'sequential'
                },
                'error_handling': {
                    'type': 'string',
                    'title': 'Error Handling',
                    'description': 'How to handle tool execution errors',
                    'enum': ['fail_fast', 'continue', 'retry'],
                    'default': 'continue'
                }
            }
        },
        'default_config': {
            'execution_mode': 'sequential',
            'error_handling': 'continue'
        },
        'input_ports': [
            {'name': 'tools', 'type': 'array', 'description': 'Tools to orchestrate', 'required': True},
            {'name': 'parameters', 'type': 'object', 'description': 'Execution parameters', 'required': False}
        ],
        'output_ports': [
            {'name': 'results', 'type': 'array', 'description': 'Tool execution results', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.mcp_orchestrator_node.MCPOrchestratorNode',
        'tags': ['mcp', 'orchestration', 'execution']
    },
    {
        'component_id': 'mcp_tool',
        'name': 'MCP Tool',
        'category': 'Tools',
        'description': 'Model Context Protocol tool integration',
        'icon_name': 'ApiOutlined',
        'color': '#531dab',
        'sort_order': 3,
        'config_schema': {
            'type': 'object',
            'properties': {
                'link': {
                    'type': 'string',
                    'title': 'MCP Tool',
                    'description': 'Select the MCP tool to execute'
                },
                'timeout': {
                    'type': 'integer',
                    'title': 'Timeout',
                    'description': 'Execution timeout in seconds',
                    'minimum': 5,
                    'maximum': 300,
                    'default': 30
                },
                'retry_count': {
                    'type': 'integer',
                    'title': 'Retry Count',
                    'description': 'Number of retries on failure',
                    'minimum': 0,
                    'maximum': 5,
                    'default': 3
                }
            },
            'required': ['link']
        },
        'default_config': {
            'timeout': 30,
            'retry_count': 3
        },
        'input_ports': [
            {'name': 'parameters', 'type': 'object', 'description': 'Tool parameters', 'required': True}
        ],
        'output_ports': [
            {'name': 'result', 'type': 'object', 'description': 'Tool execution result', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.mcp_tool_node.MCPToolNode',
        'tags': ['mcp', 'tool', 'execution']
    },
    {
        'component_id': 'rest_api',
        'name': 'Rest Api connector',
        'category': 'Tools',
        'description': 'REST API integration for external service calls',
        'icon_name': 'ApiOutlined',
        'color': '#d48806',
        'sort_order': 4,
        'config_schema': {
            'type': 'object',
            'properties': {
                'link': {
                    'type': 'string',
                    'title': 'REST API',
                    'description': 'Select the REST API to call'
                },
                'intel_link': {
                    'type': 'string',
                    'title': 'Intelligence LLM',
                    'description': 'Optional LLM for intelligent request processing'
                },
                'timeout': {
                    'type': 'integer',
                    'title': 'Timeout',
                    'description': 'Request timeout in seconds',
                    'minimum': 5,
                    'maximum': 300,
                    'default': 30
                },
                'retry_count': {
                    'type': 'integer',
                    'title': 'Retry Count',
                    'description': 'Number of retries on failure',
                    'minimum': 0,
                    'maximum': 5,
                    'default': 3
                },
                'follow_redirects': {
                    'type': 'boolean',
                    'title': 'Follow Redirects',
                    'description': 'Follow HTTP redirects automatically',
                    'default': True
                }
            },
            'required': ['link']
        },
        'default_config': {
            'timeout': 30,
            'retry_count': 3,
            'follow_redirects': True
        },
        'input_ports': [
            {'name': 'parameters', 'type': 'object', 'description': 'API request parameters', 'required': False},
            {'name': 'headers', 'type': 'object', 'description': 'HTTP headers', 'required': False},
            {'name': 'body', 'type': 'object', 'description': 'Request body data', 'required': False}
        ],
        'output_ports': [
            {'name': 'response', 'type': 'object', 'description': 'API response data', 'required': True},
            {'name': 'status_code', 'type': 'integer', 'description': 'HTTP status code', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.rest_api_node.RestApiNode',
        'tags': ['api', 'rest', 'http', 'integration']
    },
    {
        'component_id': 'condition',
        'name': 'Condition',
        'category': 'Logic',
        'description': 'Conditional branching logic',
        'icon_name': 'BranchesOutlined',
        'color': '#fa8c16',
        'sort_order': 1,
        'config_schema': {
            'type': 'object',
            'properties': {
                'condition_type': {
                    'type': 'string',
                    'title': 'Condition Type',
                    'description': 'Type of condition to evaluate',
                    'enum': ['equals', 'contains', 'greater_than', 'less_than', 'regex', 'custom'],
                    'default': 'equals'
                },
                'condition_value': {
                    'type': 'string',
                    'title': 'Condition Value',
                    'description': 'Value to compare against'
                }
            },
            'required': ['condition_type', 'condition_value']
        },
        'default_config': {
            'condition_type': 'equals'
        },
        'input_ports': [
            {'name': 'input', 'type': 'any', 'description': 'Value to evaluate', 'required': True}
        ],
        'output_ports': [
            {'name': 'true', 'type': 'any', 'description': 'Output if condition is true', 'required': False},
            {'name': 'false', 'type': 'any', 'description': 'Output if condition is false', 'required': False}
        ],
        'implementation_class': 'app.workflow.nodes.condition_node.ConditionNode',
        'tags': ['logic', 'condition', 'branching']
    },
    {
        'component_id': 'transform',
        'name': 'Transform',
        'category': 'Processing',
        'description': 'Data transformation and processing',
        'icon_name': 'NodeIndexOutlined',
        'color': '#eb2f96',
        'sort_order': 3,
        'config_schema': {
            'type': 'object',
            'properties': {
                'transform_type': {
                    'type': 'string',
                    'title': 'Transform Type',
                    'description': 'Type of transformation to apply',
                    'enum': ['json', 'text', 'array', 'custom'],
                    'default': 'json'
                },
                'transform_expression': {
                    'type': 'string',
                    'title': 'Transform Expression',
                    'description': 'Transformation expression or script'
                }
            },
            'required': ['transform_type']
        },
        'default_config': {
            'transform_type': 'json'
        },
        'input_ports': [
            {'name': 'data', 'type': 'any', 'description': 'Data to transform', 'required': True}
        ],
        'output_ports': [
            {'name': 'transformed_data', 'type': 'any', 'description': 'Transformed data', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.transform_node.TransformNode',
        'tags': ['processing', 'transform', 'data']
    },
    {
        'component_id': 'input',
        'name': 'Input',
        'category': 'IO',
        'description': 'User input collection',
        'icon_name': 'AppstoreOutlined',
        'color': '#13c2c2',
        'sort_order': 1,
        'config_schema': {
            'type': 'object',
            'properties': {
                'input_type': {
                    'type': 'string',
                    'title': 'Input Type',
                    'description': 'Type of input to collect',
                    'enum': ['text', 'number', 'boolean', 'json', 'file'],
                    'default': 'text'
                },
                'validation': {
                    'type': 'object',
                    'title': 'Validation',
                    'description': 'Input validation rules',
                    'default': {}
                }
            }
        },
        'default_config': {
            'input_type': 'text',
            'validation': {}
        },
        'input_ports': [],
        'output_ports': [
            {'name': 'user_input', 'type': 'any', 'description': 'User provided input', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.input_node.InputNode',
        'tags': ['io', 'input', 'user']
    },
    {
        'component_id': 'output',
        'name': 'Output',
        'category': 'IO',
        'description': 'Response output formatting',
        'icon_name': 'AppstoreOutlined',
        'color': '#f5222d',
        'sort_order': 2,
        'config_schema': {
            'type': 'object',
            'properties': {
                'output_format': {
                    'type': 'string',
                    'title': 'Output Format',
                    'description': 'Format for the output',
                    'enum': ['text', 'json', 'html', 'markdown'],
                    'default': 'text'
                },
                'template': {
                    'type': 'string',
                    'title': 'Template',
                    'description': 'Output template string'
                }
            }
        },
        'default_config': {
            'output_format': 'text'
        },
        'input_ports': [
            {'name': 'data', 'type': 'any', 'description': 'Data to output', 'required': True}
        ],
        'output_ports': [
            {'name': 'formatted_output', 'type': 'string', 'description': 'Formatted output', 'required': True}
        ],
        'implementation_class': 'app.workflow.nodes.output_node.OutputNode',
        'tags': ['io', 'output', 'format']
    }
]


def seed_workflow_component_definitions():
    """Seed the database with workflow component definitions"""
    db = SessionLocal()
    try:
        print("Starting to seed workflow component definitions...")
        
        for comp_data in COMPONENT_DEFINITIONS:
            # Check if component already exists
            existing = db.query(WorkflowComponentDefinition).filter(
                WorkflowComponentDefinition.component_id == comp_data['component_id']
            ).first()
            
            if existing:
                print(f"Component '{comp_data['component_id']}' already exists, skipping...")
                continue
            
            # Create new component
            component = WorkflowComponentDefinition(
                id=str(uuid4()),
                **comp_data
            )
            
            db.add(component)
            print(f"Added component: {comp_data['name']} ({comp_data['component_id']})")
        
        db.commit()
        print("Successfully seeded workflow component definitions!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding workflow component definitions: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_workflow_component_definitions()
