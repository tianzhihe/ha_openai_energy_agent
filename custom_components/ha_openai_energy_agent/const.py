"""Constants for the OpenAI Energy Management Agent integration."""

DOMAIN = "ha_openai_energy_agent"
DEFAULT_NAME = "OpenAI Energy Management Agent"
CONF_ORGANIZATION = "organization"
CONF_BASE_URL = "base_url"
DEFAULT_CONF_BASE_URL = "https://api.openai.com/v1"
CONF_API_VERSION = "api_version"
CONF_SKIP_AUTHENTICATION = "skip_authentication"
DEFAULT_SKIP_AUTHENTICATION = False

EVENT_AUTOMATION_REGISTERED = "automation_registered_via_ha_openai_energy_agent"
EVENT_CONVERSATION_FINISHED = "ha_openai_energy_agent.conversation.finished"

CONF_PROMPT = "prompt"
DEFAULT_PROMPT = """I want you to act as an intelligent Energy Management Agent for Home Assistant.

You specialize in optimizing energy consumption, managing renewable energy systems, and reducing utility costs through smart automation.

You will analyze the home's energy usage patterns, control energy-consuming devices, and provide actionable insights to maximize efficiency and minimize costs.

Current Time: {{now()}}
Location: {{ha_name}}

Available Energy-Related Devices:
```csv
entity_id,name,state,aliases
{% for entity in exposed_entities -%}
{{ entity.entity_id }},{{ entity.name }},{{ entity.state }},{{entity.aliases | join('/')}}
{% endfor -%}
```

When user ask about energy related question: Total Energy Consumption = Grid Energy + Solar Energy Generation. The sum of grid energy plus the sum of solar energy generation. When you calculate the energy consumption, you need to take solar production into account.

Energy Management Priorities:
1. Monitor real-time energy consumption and costs
2. Optimize solar panel output and battery storage
3. Schedule high-energy devices during off-peak hours
4. Maintain comfort while reducing energy waste
5. Provide cost-saving recommendations and automation suggestions

You can help users:
- Analyze energy usage patterns and identify savings opportunities
- Control smart devices to reduce energy consumption
- Optimize solar and battery systems for maximum efficiency
- Create automations for peak-hour management
- Monitor and report on energy costs and savings

Use execute_services function for device control only when requested.
Always consider energy efficiency in my recommendations.
Provide clear, actionable advice in everyday language.
Directly conduct function calls to activate tools, no need to ask users for confirmation.
"""
CONF_CHAT_MODEL = "chat_model"
DEFAULT_CHAT_MODEL = "gpt-5"
CONF_MAX_TOKENS = "max_tokens"
DEFAULT_MAX_TOKENS = 3000
CONF_TOP_P = "top_p"
DEFAULT_TOP_P = 1
CONF_TEMPERATURE = "temperature"
DEFAULT_TEMPERATURE = 1
CONF_MAX_FUNCTION_CALLS_PER_CONVERSATION = "max_function_calls_per_conversation"
DEFAULT_MAX_FUNCTION_CALLS_PER_CONVERSATION = 10
# Individual Tool Configuration Constants
CONF_USE_EXECUTE_SERVICES_TOOL = "use_execute_services_tool"
CONF_USE_GET_ENERGY_DATA_TOOL = "use_get_energy_data_tool"
CONF_USE_GET_STATISTICS_TOOL = "use_get_statistics_tool"
CONF_USE_ADD_AUTOMATION_TOOL = "use_add_automation_tool"
CONF_USE_CREATE_EVENT_TOOL = "use_create_event_tool"
CONF_USE_GET_EVENTS_TOOL = "use_get_events_tool"
CONF_USE_GET_ATTRIBUTES_TOOL = "use_get_attributes_tool"
CONF_USE_GET_AUTOMATION_TOOL = "use_get_automation_tool"
CONF_USE_ADJUST_AUTOMATION_TOOL = "use_adjust_automation_tool"

# Default tool enablement - All tools enabled by default
DEFAULT_USE_EXECUTE_SERVICES_TOOL = True
DEFAULT_USE_GET_ENERGY_DATA_TOOL = True
DEFAULT_USE_GET_STATISTICS_TOOL = True
DEFAULT_USE_ADD_AUTOMATION_TOOL = True
DEFAULT_USE_CREATE_EVENT_TOOL = True
DEFAULT_USE_GET_EVENTS_TOOL = True
DEFAULT_USE_GET_ATTRIBUTES_TOOL = True
DEFAULT_USE_GET_AUTOMATION_TOOL = True
DEFAULT_USE_ADJUST_AUTOMATION_TOOL = True

# Continuous Conversation Configuration
CONF_ENABLE_CONTINUOUS_CONVERSATION = "enable_continuous_conversation"
DEFAULT_ENABLE_CONTINUOUS_CONVERSATION = True

# GPT-5 Compatible Function Definitions with strict schema
GPT5_FUNCTION_SCHEMAS = {
    "execute_services": {
        "type": "function",
        "name": "execute_services",
        "description": "Execute energy management services for smart devices, HVAC systems, solar panels, and battery storage. Focus on energy efficiency and cost optimization.",
        "parameters": {
            "type": "object",
            "properties": {
                "list": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "The domain of the energy-related service"
                            },
                            "service": {
                                "type": "string",
                                "description": "The energy management service to be called"
                            },
                            "service_data": {
                                "type": "object",
                                "properties": {
                                    "entity_id": {
                                        "type": "string",
                                        "description": "The entity_id of the energy device. Must start with domain, followed by dot character."
                                    }
                                },
                                "required": ["entity_id"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["domain", "service", "service_data"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["list"],
            "additionalProperties": False
        },
        "strict": False
    },
    "get_energy_statistic_ids": {
        "type": "function",
        "name": "get_energy_statistic_ids",
        "description": "Get energy statistic IDs for analysis and monitoring",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    "get_statistics": {
        "type": "function",
        "name": "get_statistics",
        "description": "Get energy statistics for specified time periods and devices",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "The start datetime"
                },
                "end_time": {
                    "type": "string",
                    "description": "The end datetime"
                },
                "statistic_ids": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "The statistic IDs"
                    }
                },
                "period": {
                    "type": "string",
                    "description": "The period",
                    "enum": ["day", "week", "month"]
                }
            },
            "required": ["start_time", "end_time", "statistic_ids", "period"],
            "additionalProperties": False
        },
        "strict": True
    },
    "add_automation": {
        "type": "function",
        "name": "add_automation",
        "description": "Add energy-saving automation to Home Assistant",
        "parameters": {
            "type": "object",
            "properties": {
                "automation_config": {
                    "type": "string",
                    "description": "A configuration for automation in valid YAML format. Use \\n for line breaks."
                }
            },
            "required": ["automation_config"],
            "additionalProperties": False
        },
        "strict": True
    },
    "create_event": {
        "type": "function",
        "name": "create_event",
        "description": "Create calendar events for energy management scheduling",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Event summary or subject"
                },
                "start_date_time": {
                    "type": "string",
                    "description": "Event start date and time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                "end_date_time": {
                    "type": "string",
                    "description": "Event end date and time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                }
            },
            "required": ["summary", "start_date_time", "end_date_time"],
            "additionalProperties": False
        },
        "strict": True
    },
    "get_events": {
        "type": "function",
        "name": "get_events",
        "description": "Get calendar events for energy management scheduling",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date_time": {
                    "type": "string",
                    "description": "Start date time in '%Y-%m-%dT%H:%M:%S%z' format"
                },
                "end_date_time": {
                    "type": "string",
                    "description": "End date time in '%Y-%m-%dT%H:%M:%S%z' format"
                }
            },
            "required": ["start_date_time", "end_date_time"],
            "additionalProperties": False
        },
        "strict": True
    },
    "get_attributes": {
        "type": "function",
        "name": "get_attributes",
        "description": "Get detailed attributes of Home Assistant energy entities",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The entity ID to get attributes for"
                }
            },
            "required": ["entity_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    "get_automation": {
        "type": "function",
        "name": "get_automation",
        "description": "Retrieve existing Home Assistant automations and their configurations",
        "parameters": {
            "type": "object",
            "properties": {
                "automation_id": {
                    "type": "string",
                    "description": "Optional specific automation entity ID to retrieve (e.g., 'automation.energy_saver'). If not provided, returns all automations."
                }
            },
            "additionalProperties": False
        },
        "strict": False
    },
    "adjust_automation": {
        "type": "function",
        "name": "adjust_automation",
        "description": "Modify, enable, disable, or delete existing Home Assistant automations",
        "parameters": {
            "type": "object",
            "properties": {
                "automation_id": {
                    "type": "string",
                    "description": "The automation entity ID to modify (e.g., 'automation.energy_saver')"
                },
                "action": {
                    "type": "string",
                    "description": "Action to perform on the automation",
                    "enum": ["enable", "disable", "delete", "update"]
                },
                "new_config": {
                    "type": "string",
                    "description": "New automation configuration in YAML format (required for 'update' action)"
                }
            },
            "required": ["automation_id", "action"],
            "additionalProperties": False
        },
        "strict": True
    }
}

# Legacy support - will be deprecated
CONF_FUNCTIONS = "functions"
DEFAULT_CONF_FUNCTIONS = []
CONF_ATTACH_USERNAME = "attach_username"
DEFAULT_ATTACH_USERNAME = False
CONF_USE_TOOLS = "use_tools"
DEFAULT_USE_TOOLS = False
CONF_CONTEXT_THRESHOLD = "context_threshold"
DEFAULT_CONTEXT_THRESHOLD = 13000
CONTEXT_TRUNCATE_STRATEGIES = [{"key": "clear", "label": "Clear All Messages"}]
CONF_CONTEXT_TRUNCATE_STRATEGY = "context_truncate_strategy"
DEFAULT_CONTEXT_TRUNCATE_STRATEGY = CONTEXT_TRUNCATE_STRATEGIES[0]["key"]

SERVICE_QUERY_IMAGE = "query_image"

CONF_PAYLOAD_TEMPLATE = "payload_template"
