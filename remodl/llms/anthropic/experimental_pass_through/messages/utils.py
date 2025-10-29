from typing import Any, Dict, List, cast, get_type_hints

from remodl.types.llms.anthropic import AnthropicMessagesRequestOptionalParams
from remodl.types.llms.anthropic_messages.anthropic_response import (
    AnthropicMessagesResponse,
)


class AnthropicMessagesRequestUtils:
    @staticmethod
    def get_requested_anthropic_messages_optional_param(
        params: Dict[str, Any],
    ) -> AnthropicMessagesRequestOptionalParams:
        """
        Filter parameters to only include those defined in AnthropicMessagesRequestOptionalParams.

        Args:
            params: Dictionary of parameters to filter

        Returns:
            AnthropicMessagesRequestOptionalParams instance with only the valid parameters
        """
        valid_keys = get_type_hints(AnthropicMessagesRequestOptionalParams).keys()
        filtered_params = {
            k: v for k, v in params.items() if k in valid_keys and v is not None
        }
        return cast(AnthropicMessagesRequestOptionalParams, filtered_params)


def mock_response(
    model: str,
    messages: List[Dict],
    max_tokens: int,
    mock_response: str = "Hi! My name is Claude.",
    **kwargs,
) -> AnthropicMessagesResponse:
    """
    Mock response for Anthropic messages
    """
    from remodl.exceptions import (
        ContextWindowExceededError,
        InternalServerError,
        RateLimitError,
    )

    if mock_response == "remodl.InternalServerError":
        raise InternalServerError(
            message="this is a mock internal server error",
            llm_provider="anthropic",
            model=model,
        )
    elif mock_response == "remodl.ContextWindowExceededError":
        raise ContextWindowExceededError(
            message="this is a mock context window exceeded error",
            llm_provider="anthropic",
            model=model,
        )
    elif mock_response == "remodl.RateLimitError":
        raise RateLimitError(
            message="this is a mock rate limit error",
            llm_provider="anthropic",
            model=model,
        )
    return AnthropicMessagesResponse(
        **{
            "content": [{"text": mock_response, "type": "text"}],
            "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
            "model": "claude-sonnet-4-20250514",
            "role": "assistant",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "type": "message",
            "usage": {"input_tokens": 2095, "output_tokens": 503},
        }
    )
