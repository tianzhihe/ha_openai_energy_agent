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
I specialize in optimizing energy consumption, managing renewable energy systems, and reducing utility costs through smart automation.

I will analyze your home's energy usage patterns, control energy-consuming devices, and provide actionable insights to maximize efficiency and minimize costs.

Current Time: {{now()}}
Location: {{ha_name}}

Available Energy-Related Devices:
```csv
entity_id,name,state,aliases
{% for entity in exposed_entities -%}
{{ entity.entity_id }},{{ entity.name }},{{ entity.state }},{{entity.aliases | join('/')}}
{% endfor -%}
```

Energy Management Priorities:
1. Monitor real-time energy consumption and costs
2. Optimize solar panel output and battery storage
3. Schedule high-energy devices during off-peak hours
4. Maintain comfort while reducing energy waste
5. Provide cost-saving recommendations and automation suggestions

I can help you:
- Analyze energy usage patterns and identify savings opportunities
- Control smart devices to reduce energy consumption
- Optimize solar and battery systems for maximum efficiency
- Create automations for peak-hour management
- Monitor and report on energy costs and savings

Use execute_services function for device control only when requested.
Always consider energy efficiency in my recommendations.
Provide clear, actionable advice in everyday language.
"""
CONF_CHAT_MODEL = "chat_model"
DEFAULT_CHAT_MODEL = "gpt-5"
CONF_MAX_TOKENS = "max_tokens"
DEFAULT_MAX_TOKENS = 150
CONF_TOP_P = "top_p"
DEFAULT_TOP_P = 1
CONF_TEMPERATURE = "temperature"
DEFAULT_TEMPERATURE = 0.5
CONF_MAX_FUNCTION_CALLS_PER_CONVERSATION = "max_function_calls_per_conversation"
DEFAULT_MAX_FUNCTION_CALLS_PER_CONVERSATION = 1
CONF_FUNCTIONS = "functions"
DEFAULT_CONF_FUNCTIONS = [
    {
        "spec": {
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
                                    "description": "The domain of the energy-related service (e.g., switch, climate, sensor, solar, battery)",
                                },
                                "service": {
                                    "type": "string",
                                    "description": "The energy management service to be called (e.g., turn_on, turn_off, set_temperature, optimize)",
                                },
                                "service_data": {
                                    "type": "object",
                                    "description": "Service data for energy device control and optimization.",
                                    "properties": {
                                        "entity_id": {
                                            "type": "string",
                                            "description": "The entity_id of the energy device. Must start with domain, followed by dot character.",
                                        }
                                    },
                                    "required": ["entity_id"],
                                },
                            },
                            "required": ["domain", "service", "service_data"],
                        },
                    }
                },
            },
        },
        "function": {"type": "native", "name": "execute_service"},
    }
]
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
