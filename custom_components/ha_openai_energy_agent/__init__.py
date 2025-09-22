"""The OpenAI Energy Management Agent integration."""

from __future__ import annotations

import json
import logging
from typing import Literal

from openai import AsyncAzureOpenAI, AsyncOpenAI
from openai._exceptions import AuthenticationError, OpenAIError
from openai.types.chat.chat_completion import (
    ChatCompletion,
    ChatCompletionMessage,
    Choice,
)
import yaml

from homeassistant.components import conversation
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, CONF_API_KEY, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryNotReady,
    HomeAssistantError,
    TemplateError,
)
from homeassistant.helpers import (
    config_validation as cv,
    entity_registry as er,
    intent,
    template,
)
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import ulid

from .const import (
    CONF_API_VERSION,
    CONF_ATTACH_USERNAME,
    CONF_BASE_URL,
    CONF_CHAT_MODEL,
    CONF_CONTEXT_THRESHOLD,
    CONF_CONTEXT_TRUNCATE_STRATEGY,
    CONF_FUNCTIONS,
    CONF_MAX_FUNCTION_CALLS_PER_CONVERSATION,
    CONF_MAX_TOKENS,
    CONF_ORGANIZATION,
    CONF_PROMPT,
    CONF_SKIP_AUTHENTICATION,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_USE_TOOLS,
    CONF_USE_EXECUTE_SERVICES_TOOL,
    CONF_USE_GET_ENERGY_DATA_TOOL,
    CONF_USE_GET_STATISTICS_TOOL,
    CONF_USE_ADD_AUTOMATION_TOOL,
    CONF_USE_CREATE_EVENT_TOOL,
    CONF_USE_GET_EVENTS_TOOL,
    CONF_USE_GET_ATTRIBUTES_TOOL,
    DEFAULT_ATTACH_USERNAME,
    DEFAULT_CHAT_MODEL,
    DEFAULT_CONF_FUNCTIONS,
    DEFAULT_CONTEXT_THRESHOLD,
    DEFAULT_CONTEXT_TRUNCATE_STRATEGY,
    DEFAULT_MAX_FUNCTION_CALLS_PER_CONVERSATION,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROMPT,
    DEFAULT_SKIP_AUTHENTICATION,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_USE_TOOLS,
    DEFAULT_USE_EXECUTE_SERVICES_TOOL,
    DEFAULT_USE_GET_ENERGY_DATA_TOOL,
    DEFAULT_USE_GET_STATISTICS_TOOL,
    DEFAULT_USE_ADD_AUTOMATION_TOOL,
    DEFAULT_USE_CREATE_EVENT_TOOL,
    DEFAULT_USE_GET_EVENTS_TOOL,
    DEFAULT_USE_GET_ATTRIBUTES_TOOL,
    DOMAIN,
    EVENT_CONVERSATION_FINISHED,
    GPT5_FUNCTION_SCHEMAS,
)
from .exceptions import (
    FunctionLoadFailed,
    FunctionNotFound,
    InvalidFunction,
    ParseArgumentsFailed,
    TokenLengthExceededError,
)
from .helpers import get_function_executor, is_azure, validate_authentication
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


# hass.data key for agent.
DATA_AGENT = "agent"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up OpenAI Energy Management Agent."""
    await async_setup_services(hass, config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAI Energy Management Agent from a config entry."""

    try:
        await validate_authentication(
            hass=hass,
            api_key=entry.data[CONF_API_KEY],
            base_url=entry.data.get(CONF_BASE_URL),
            api_version=entry.data.get(CONF_API_VERSION),
            organization=entry.data.get(CONF_ORGANIZATION),
            skip_authentication=entry.data.get(
                CONF_SKIP_AUTHENTICATION, DEFAULT_SKIP_AUTHENTICATION
            ),
        )
    except AuthenticationError as err:
        _LOGGER.error("Invalid API key: %s", err)
        return False
    except OpenAIError as err:
        raise ConfigEntryNotReady(err) from err

    agent = OpenAIAgent(hass, entry)

    data = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    data[CONF_API_KEY] = entry.data[CONF_API_KEY]
    data[DATA_AGENT] = agent

    conversation.async_set_agent(hass, entry, agent)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenAI Energy Management Agent."""
    hass.data[DOMAIN].pop(entry.entry_id)
    conversation.async_unset_agent(hass, entry)
    return True


class OpenAIAgent(conversation.AbstractConversationAgent):
    """OpenAI Energy Management conversation agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Energy Management AI agent."""
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[dict]] = {}
        base_url = entry.data.get(CONF_BASE_URL)
        if is_azure(base_url):
            self.client = AsyncAzureOpenAI(
                api_key=entry.data[CONF_API_KEY],
                azure_endpoint=base_url,
                api_version=entry.data.get(CONF_API_VERSION),
                organization=entry.data.get(CONF_ORGANIZATION),
                http_client=get_async_client(hass),
            )
        else:
            self.client = AsyncOpenAI(
                api_key=entry.data[CONF_API_KEY],
                base_url=base_url,
                organization=entry.data.get(CONF_ORGANIZATION),
                http_client=get_async_client(hass),
            )
        # Cache current platform data which gets added to each request (caching done by library)
        _ = hass.async_add_executor_job(self.client.platform_headers)

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        exposed_entities = self.get_exposed_entities()

        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            user_input.conversation_id = conversation_id
            try:
                system_message = self._generate_system_message(
                    exposed_entities, user_input
                )
            except TemplateError as err:
                _LOGGER.error("Error rendering prompt: %s", err)
                intent_response = intent.IntentResponse(language=user_input.language)
                intent_response.async_set_error(
                    intent.IntentResponseErrorCode.UNKNOWN,
                    f"Sorry, I had a problem with my template: {err}",
                )
                return conversation.ConversationResult(
                    response=intent_response, conversation_id=conversation_id
                )
            messages = [system_message]
        user_message = {"role": "user", "content": user_input.text}
        if self.entry.options.get(CONF_ATTACH_USERNAME, DEFAULT_ATTACH_USERNAME):
            user = user_input.context.user_id
            if user is not None:
                user_message[ATTR_NAME] = user

        messages.append(user_message)

        try:
            query_response = await self.query(user_input, messages, exposed_entities, 0)
        except OpenAIError as err:
            _LOGGER.error(err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Sorry, I had a problem talking to OpenAI: {err}",
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )
        except HomeAssistantError as err:
            _LOGGER.error(err, exc_info=err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Something went wrong: {err}",
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )

        messages.append(query_response.message.model_dump(exclude_none=True))
        self.history[conversation_id] = messages

        self.hass.bus.async_fire(
            EVENT_CONVERSATION_FINISHED,
            {
                "response": query_response.response.model_dump(),
                "user_input": user_input,
                "messages": messages,
            },
        )

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(query_response.message.content)
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    def _generate_system_message(
        self, exposed_entities, user_input: conversation.ConversationInput
    ):
        raw_prompt = self.entry.options.get(CONF_PROMPT, DEFAULT_PROMPT)
        prompt = self._async_generate_prompt(raw_prompt, exposed_entities, user_input)
        return {"role": "system", "content": prompt}

    def _async_generate_prompt(
        self,
        raw_prompt: str,
        exposed_entities,
        user_input: conversation.ConversationInput,
    ) -> str:
        """Generate a prompt for the user."""
        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
                "exposed_entities": exposed_entities,
                "current_device_id": user_input.device_id,
            },
            parse_result=False,
        )

    def get_exposed_entities(self):
        states = [
            state
            for state in self.hass.states.async_all()
            if async_should_expose(self.hass, conversation.DOMAIN, state.entity_id)
        ]
        entity_registry = er.async_get(self.hass)
        exposed_entities = []
        for state in states:
            entity_id = state.entity_id
            entity = entity_registry.async_get(entity_id)

            aliases = []
            if entity and entity.aliases:
                aliases = entity.aliases

            exposed_entities.append(
                {
                    "entity_id": entity_id,
                    "name": state.name,
                    "state": self.hass.states.get(entity_id).state,
                    "aliases": aliases,
                }
            )
        return exposed_entities

    def get_functions(self):
        """Get enabled functions based on individual tool toggles."""
        enabled_functions = []
        
        # Map of tool configs to function schemas and executors
        tool_mapping = {
            CONF_USE_EXECUTE_SERVICES_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["execute_services"],
                "executor": {"type": "native", "name": "execute_service"}
            },
            CONF_USE_GET_ENERGY_DATA_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["get_energy_statistic_ids"],
                "executor": {"type": "native", "name": "get_energy"}
            },
            CONF_USE_GET_STATISTICS_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["get_statistics"],
                "executor": {"type": "native", "name": "get_statistics"}
            },
            CONF_USE_ADD_AUTOMATION_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["add_automation"],
                "executor": {"type": "native", "name": "add_automation"}
            },
            CONF_USE_CREATE_EVENT_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["create_event"],
                "executor": {"type": "script", "sequence": [{"service": "calendar.create_event"}]}
            },
            CONF_USE_GET_EVENTS_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["get_events"],
                "executor": {"type": "script", "sequence": [{"service": "calendar.get_events"}]}
            },
            CONF_USE_GET_ATTRIBUTES_TOOL: {
                "schema": GPT5_FUNCTION_SCHEMAS["get_attributes"],
                "executor": {"type": "template", "value_template": "{{ states[entity_id] }}"}
            }
        }
        
        # Check each tool toggle and add enabled functions
        for tool_conf, tool_data in tool_mapping.items():
            # Get the default value for each tool
            default_value = {
                CONF_USE_EXECUTE_SERVICES_TOOL: DEFAULT_USE_EXECUTE_SERVICES_TOOL,
                CONF_USE_GET_ENERGY_DATA_TOOL: DEFAULT_USE_GET_ENERGY_DATA_TOOL,
                CONF_USE_GET_STATISTICS_TOOL: DEFAULT_USE_GET_STATISTICS_TOOL,
                CONF_USE_ADD_AUTOMATION_TOOL: DEFAULT_USE_ADD_AUTOMATION_TOOL,
                CONF_USE_CREATE_EVENT_TOOL: DEFAULT_USE_CREATE_EVENT_TOOL,
                CONF_USE_GET_EVENTS_TOOL: DEFAULT_USE_GET_EVENTS_TOOL,
                CONF_USE_GET_ATTRIBUTES_TOOL: DEFAULT_USE_GET_ATTRIBUTES_TOOL,
            }.get(tool_conf, False)
            
            if self.entry.options.get(tool_conf, default_value):
                try:
                    function_executor = get_function_executor(tool_data["executor"]["type"])
                    processed_executor = function_executor.to_arguments(tool_data["executor"])
                    
                    enabled_functions.append({
                        "spec": tool_data["schema"],
                        "function": processed_executor
                    })
                except (InvalidFunction, FunctionNotFound) as e:
                    _LOGGER.warning("Failed to load function %s: %s", tool_data["schema"]["name"], e)
                    continue
                except Exception as e:
                    _LOGGER.warning("Unexpected error loading function %s: %s", tool_data["schema"]["name"], e)
                    continue
        
        return enabled_functions

    async def truncate_message_history(
        self, messages, exposed_entities, user_input: conversation.ConversationInput
    ):
        """Truncate message history."""
        strategy = self.entry.options.get(
            CONF_CONTEXT_TRUNCATE_STRATEGY, DEFAULT_CONTEXT_TRUNCATE_STRATEGY
        )

        if strategy == "clear":
            last_user_message_index = None
            for i in reversed(range(len(messages))):
                if messages[i]["role"] == "user":
                    last_user_message_index = i
                    break

            if last_user_message_index is not None:
                del messages[1:last_user_message_index]
                # refresh system prompt when all messages are deleted
                messages[0] = self._generate_system_message(
                    exposed_entities, user_input
                )

    async def query(
        self,
        user_input: conversation.ConversationInput,
        messages,
        exposed_entities,
        n_requests,
    ) -> OpenAIQueryResponse:
        """Process a sentence using appropriate API for model version."""
        model = self.entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        max_tokens = self.entry.options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
        top_p = self.entry.options.get(CONF_TOP_P, DEFAULT_TOP_P)
        temperature = self.entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        context_threshold = self.entry.options.get(
            CONF_CONTEXT_THRESHOLD, DEFAULT_CONTEXT_THRESHOLD
        )
        functions = list(map(lambda s: s["spec"], self.get_functions()))
        
        _LOGGER.info("Prompt for %s: %s", model, json.dumps(messages))

        # Check if this is GPT-5 or newer model
        if model.startswith("gpt-5") or model.startswith("o1"):
            return await self._query_gpt5(
                user_input, messages, exposed_entities, n_requests, model, max_tokens, 
                top_p, temperature, context_threshold, functions
            )
        else:
            return await self._query_legacy(
                user_input, messages, exposed_entities, n_requests, model, max_tokens,
                top_p, temperature, context_threshold, functions
            )

    async def _query_gpt5(
        self, user_input, messages, exposed_entities, n_requests, model, max_tokens,
        top_p, temperature, context_threshold, functions
    ) -> OpenAIQueryResponse:
        """Handle GPT-5 API calls using responses.create()."""
        try:
            # Convert messages format for GPT-5 input
            input_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
            
            # Prepare tools for GPT-5
            tools = functions if functions else []
            
            # GPT-5 uses responses.create() API
            response = await self.client.responses.create(
                model=model,
                input=input_messages,
                tools=tools,
                max_completion_tokens=max_tokens,
            )
            
            _LOGGER.info("GPT-5 Response: %s", json.dumps(response.model_dump(exclude_none=True)))
            
            # Process GPT-5 response format
            if response.output and len(response.output) > 0:
                output = response.output[0]
                
                # Check if there are tool calls
                if hasattr(output, 'tool_calls') and output.tool_calls:
                    # Handle function calls
                    return await self._execute_gpt5_tool_calls(
                        user_input, messages, output, exposed_entities, n_requests + 1
                    )
                else:
                    # Regular text response
                    message = ChatCompletionMessage(
                        role="assistant",
                        content=output.content if hasattr(output, 'content') else str(output)
                    )
                    # Create a mock response object for compatibility
                    mock_response = type('MockResponse', (), {
                        'usage': type('Usage', (), {'total_tokens': 0})(),
                        'choices': [type('Choice', (), {'message': message})()]
                    })()
                    return OpenAIQueryResponse(response=mock_response, message=message)
            
        except Exception as e:
            _LOGGER.error("GPT-5 API call failed: %s", e)
            # Fallback to legacy API
            return await self._query_legacy(
                user_input, messages, exposed_entities, n_requests, model, max_tokens,
                top_p, temperature, context_threshold, functions
            )

    async def _query_legacy(
        self, user_input, messages, exposed_entities, n_requests, model, max_tokens,
        top_p, temperature, context_threshold, functions
    ) -> OpenAIQueryResponse:
        """Handle legacy API calls using chat.completions.create()."""
        use_tools = self.entry.options.get(CONF_USE_TOOLS, DEFAULT_USE_TOOLS)
        function_call = "auto"
        if n_requests == self.entry.options.get(
            CONF_MAX_FUNCTION_CALLS_PER_CONVERSATION,
            DEFAULT_MAX_FUNCTION_CALLS_PER_CONVERSATION,
        ):
            function_call = "none"

        tool_kwargs = {"functions": functions, "function_call": function_call}
        if use_tools:
            tool_kwargs = {
                "tools": [{"type": "function", "function": func} for func in functions],
                "tool_choice": function_call,
            }

        if len(functions) == 0:
            tool_kwargs = {}

        # Legacy models use max_tokens
        token_param = {"max_tokens": max_tokens}

        response: ChatCompletion = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            top_p=top_p,
            temperature=temperature,
            user=user_input.conversation_id,
            **token_param,
            **tool_kwargs,
        )

        _LOGGER.info("Legacy Response: %s", json.dumps(response.model_dump(exclude_none=True)))

        if response.usage.total_tokens > context_threshold:
            await self.truncate_message_history(messages, exposed_entities, user_input)

        choice: Choice = response.choices[0]
        message = choice.message

        if choice.finish_reason == "function_call":
            return await self.execute_function_call(
                user_input, messages, message, exposed_entities, n_requests + 1
            )
        if choice.finish_reason == "tool_calls":
            return await self.execute_tool_calls(
                user_input, messages, message, exposed_entities, n_requests + 1
            )
        if choice.finish_reason == "length":
            raise TokenLengthExceededError(response.usage.completion_tokens)

        return OpenAIQueryResponse(response=response, message=message)

    async def _execute_gpt5_tool_calls(
        self, user_input, messages, output, exposed_entities, n_requests
    ) -> OpenAIQueryResponse:
        """Execute GPT-5 tool calls."""
        try:
            # Add the assistant's message with tool calls to history
            messages.append({
                "role": "assistant", 
                "content": output.content if hasattr(output, 'content') else "",
                "tool_calls": [tool_call.model_dump() for tool_call in output.tool_calls]
            })
            
            # Execute each tool call
            for tool_call in output.tool_calls:
                function_name = tool_call.function.name if hasattr(tool_call, 'function') else tool_call.name
                function = next(
                    (s for s in self.get_functions() if s["spec"]["name"] == function_name),
                    None,
                )
                
                if function is not None:
                    result = await self.execute_tool_function(
                        user_input, tool_call, exposed_entities, function
                    )
                    
                    messages.append({
                        "tool_call_id": tool_call.id if hasattr(tool_call, 'id') else str(hash(function_name)),
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    })
                else:
                    _LOGGER.error("Function not found: %s", function_name)
                    messages.append({
                        "tool_call_id": tool_call.id if hasattr(tool_call, 'id') else str(hash(function_name)),
                        "role": "tool", 
                        "name": function_name,
                        "content": f"Error: Function {function_name} not found",
                    })
            
            # Continue conversation with updated messages
            return await self.query(user_input, messages, exposed_entities, n_requests)
            
        except Exception as e:
            _LOGGER.error("Error executing GPT-5 tool calls: %s", e)
            # Return a basic response
            message = ChatCompletionMessage(
                role="assistant",
                content=f"I encountered an error while processing your request: {e}"
            )
            mock_response = type('MockResponse', (), {
                'usage': type('Usage', (), {'total_tokens': 0})(),
                'choices': [type('Choice', (), {'message': message})()]
            })()
            return OpenAIQueryResponse(response=mock_response, message=message)

    async def execute_function_call(
        self,
        user_input: conversation.ConversationInput,
        messages,
        message: ChatCompletionMessage,
        exposed_entities,
        n_requests,
    ) -> OpenAIQueryResponse:
        function_name = message.function_call.name
        function = next(
            (s for s in self.get_functions() if s["spec"]["name"] == function_name),
            None,
        )
        if function is not None:
            return await self.execute_function(
                user_input,
                messages,
                message,
                exposed_entities,
                n_requests,
                function,
            )
        raise FunctionNotFound(function_name)

    async def execute_function(
        self,
        user_input: conversation.ConversationInput,
        messages,
        message: ChatCompletionMessage,
        exposed_entities,
        n_requests,
        function,
    ) -> OpenAIQueryResponse:
        function_executor = get_function_executor(function["function"]["type"])

        try:
            arguments = json.loads(message.function_call.arguments)
        except json.decoder.JSONDecodeError as err:
            raise ParseArgumentsFailed(message.function_call.arguments) from err

        result = await function_executor.execute(
            self.hass, function["function"], arguments, user_input, exposed_entities
        )

        messages.append(
            {
                "role": "function",
                "name": message.function_call.name,
                "content": str(result),
            }
        )
        return await self.query(user_input, messages, exposed_entities, n_requests)

    async def execute_tool_calls(
        self,
        user_input: conversation.ConversationInput,
        messages,
        message: ChatCompletionMessage,
        exposed_entities,
        n_requests,
    ) -> OpenAIQueryResponse:
        messages.append(message.model_dump(exclude_none=True))
        for tool in message.tool_calls:
            function_name = tool.function.name
            function = next(
                (s for s in self.get_functions() if s["spec"]["name"] == function_name),
                None,
            )
            if function is not None:
                result = await self.execute_tool_function(
                    user_input,
                    tool,
                    exposed_entities,
                    function,
                )

                messages.append(
                    {
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )
            else:
                raise FunctionNotFound(function_name)
        return await self.query(user_input, messages, exposed_entities, n_requests)

    async def execute_tool_function(
        self,
        user_input: conversation.ConversationInput,
        tool,
        exposed_entities,
        function,
    ) -> OpenAIQueryResponse:
        function_executor = get_function_executor(function["function"]["type"])

        try:
            arguments = json.loads(tool.function.arguments)
        except json.decoder.JSONDecodeError as err:
            raise ParseArgumentsFailed(tool.function.arguments) from err

        result = await function_executor.execute(
            self.hass, function["function"], arguments, user_input, exposed_entities
        )
        return result


class OpenAIQueryResponse:
    """OpenAI query response value object."""

    def __init__(
        self, response: ChatCompletion, message: ChatCompletionMessage
    ) -> None:
        """Initialize OpenAI query response value object."""
        self.response = response
        self.message = message
