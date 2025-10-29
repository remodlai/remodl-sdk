# +-----------------------------------------------+
# |                                               |
# |           Give Feedback / Get Help            |
# | https://github.com/BerriAI/remodl/issues/new |
# |                                               |
# +-----------------------------------------------+
#
#  Thank you users! We ❤️ you! - Krrish & Ishaan

import copy
from typing import TYPE_CHECKING, Any, Optional

import remodl
from remodl.integrations.custom_logger import CustomLogger
from remodl.secret_managers.main import str_to_bool
from remodl.types.utils import StandardCallbackDynamicParams
from remodl.remodl_core_utils.core_helpers import (
    get_metadata_variable_name_from_kwargs,
)
import asyncio

if TYPE_CHECKING:
    from remodl.remodl_core_utils.remodl_logging import (
        Logging as _LiteLLMLoggingObject,
    )

    LiteLLMLoggingObject = _LiteLLMLoggingObject
else:
    LiteLLMLoggingObject = Any


def redact_message_input_output_from_custom_logger(
    remodl_logging_obj: LiteLLMLoggingObject, result, custom_logger: CustomLogger
):
    if (
        hasattr(custom_logger, "message_logging")
        and custom_logger.message_logging is not True
    ):
        return perform_redaction(remodl_logging_obj.model_call_details, result)
    return result


def _redact_choice_content(choice):
    """Helper to redact content in a choice (message or delta)."""
    if isinstance(choice, remodl.Choices):
        choice.message.content = "redacted-by-remodl"
        if hasattr(choice.message, "reasoning_content"):
            choice.message.reasoning_content = "redacted-by-remodl"
        if hasattr(choice.message, "thinking_blocks"):
            choice.message.thinking_blocks = None
    elif isinstance(choice, remodl.utils.StreamingChoices):
        choice.delta.content = "redacted-by-remodl"
        if hasattr(choice.delta, "reasoning_content"):
            choice.delta.reasoning_content = "redacted-by-remodl"
        if hasattr(choice.delta, "thinking_blocks"):
            choice.delta.thinking_blocks = None


def _redact_responses_api_output(output_items):
    """Helper to redact ResponsesAPIResponse output items."""
    for output_item in output_items:
        if hasattr(output_item, "content") and isinstance(output_item.content, list):
            for content_part in output_item.content:
                if hasattr(content_part, "text"):
                    content_part.text = "redacted-by-remodl"
        
        # Redact reasoning items in output array
        if hasattr(output_item, "type") and output_item.type == "reasoning":
            if hasattr(output_item, "summary") and isinstance(output_item.summary, list):
                for summary_item in output_item.summary:
                    if hasattr(summary_item, "text"):
                        summary_item.text = "redacted-by-remodl"


def perform_redaction(model_call_details: dict, result):
    """
    Performs the actual redaction on the logging object and result.
    """
    # Redact model_call_details
    model_call_details["messages"] = [
        {"role": "user", "content": "redacted-by-remodl"}
    ]
    model_call_details["prompt"] = ""
    model_call_details["input"] = ""

    # Redact streaming response
    if (
        model_call_details.get("stream", False) is True
        and "complete_streaming_response" in model_call_details
    ):
        _streaming_response = model_call_details["complete_streaming_response"]
        if hasattr(_streaming_response, "choices"):
            for choice in _streaming_response.choices:
                _redact_choice_content(choice)
        elif hasattr(_streaming_response, "output"):
            _redact_responses_api_output(_streaming_response.output)
            # Redact reasoning field in ResponsesAPIResponse
            if hasattr(_streaming_response, "reasoning") and _streaming_response.reasoning is not None:
                _streaming_response.reasoning = None

    # Redact result
    if result is not None:
        # Check if result is a coroutine, async generator, or other async object - these cannot be deepcopied
        if (asyncio.iscoroutine(result) or 
            asyncio.iscoroutinefunction(result) or
            hasattr(result, '__aiter__') or  # async generator
            hasattr(result, '__anext__')):   # async iterator
            # For async objects, return a simple redacted response without deepcopy
            return {"text": "redacted-by-remodl"}
        
        _result = copy.deepcopy(result)
        if isinstance(_result, remodl.ModelResponse):
            if hasattr(_result, "choices") and _result.choices is not None:
                for choice in _result.choices:
                    _redact_choice_content(choice)
        elif isinstance(_result, remodl.ResponsesAPIResponse):
            if hasattr(_result, "output"):
                _redact_responses_api_output(_result.output)
            # Redact reasoning field in ResponsesAPIResponse
            if hasattr(_result, "reasoning") and _result.reasoning is not None:
                _result.reasoning = None
        elif isinstance(_result, remodl.EmbeddingResponse):
            if hasattr(_result, "data") and _result.data is not None:
                _result.data = []
        else:
            return {"text": "redacted-by-remodl"}
        return _result


def should_redact_message_logging(model_call_details: dict) -> bool:
    """
    Determine if message logging should be redacted.
    """
    remodl_params = model_call_details.get("remodl_params", {})
    
    metadata_field = get_metadata_variable_name_from_kwargs(remodl_params)
    metadata = remodl_params.get(metadata_field, {})
    
    # Get headers from the metadata
    request_headers = metadata.get("headers", {}) if isinstance(metadata, dict) else {}

    possible_request_headers = [
        "remodl-enable-message-redaction",  # old header. maintain backwards compatibility
        "x-remodl-enable-message-redaction",  # new header
    ]

    is_redaction_enabled_via_header = False
    for header in possible_request_headers:
        if bool(request_headers.get(header, False)):
            is_redaction_enabled_via_header = True
            break

    # check if user opted out of logging message/response to callbacks
    if (
        remodl.turn_off_message_logging is not True
        and is_redaction_enabled_via_header is not True
        and _get_turn_off_message_logging_from_dynamic_params(model_call_details)
        is not True
    ):
        return False

    if request_headers and bool(
        request_headers.get("remodl-disable-message-redaction", False)
    ):
        return False

    # user has OPTED OUT of message redaction
    if _get_turn_off_message_logging_from_dynamic_params(model_call_details) is False:
        return False

    return True


def redact_message_input_output_from_logging(
    model_call_details: dict, result, input: Optional[Any] = None
) -> Any:
    """
    Removes messages, prompts, input, response from logging. This modifies the data in-place
    only redacts when remodl.turn_off_message_logging == True
    """
    if should_redact_message_logging(model_call_details):
        return perform_redaction(model_call_details, result)
    return result


def _get_turn_off_message_logging_from_dynamic_params(
    model_call_details: dict,
) -> Optional[bool]:
    """
    gets the value of `turn_off_message_logging` from the dynamic params, if it exists.

    handles boolean and string values of `turn_off_message_logging`
    """
    standard_callback_dynamic_params: Optional[StandardCallbackDynamicParams] = (
        model_call_details.get("standard_callback_dynamic_params", None)
    )
    if standard_callback_dynamic_params:
        _turn_off_message_logging = standard_callback_dynamic_params.get(
            "turn_off_message_logging"
        )
        if isinstance(_turn_off_message_logging, bool):
            return _turn_off_message_logging
        elif isinstance(_turn_off_message_logging, str):
            return str_to_bool(_turn_off_message_logging)
    return None


def redact_user_api_key_info(metadata: dict) -> dict:
    """
    removes any user_api_key_info before passing to logging object, if flag set

    Usage:

    SDK
    ```python
    remodl.redact_user_api_key_info = True
    ```

    PROXY:
    ```yaml
    remodl_settings:
        redact_user_api_key_info: true
    ```
    """
    if remodl.redact_user_api_key_info is not True:
        return metadata

    new_metadata = {}
    for k, v in metadata.items():
        if isinstance(k, str) and k.startswith("user_api_key"):
            pass
        else:
            new_metadata[k] = v

    return new_metadata
