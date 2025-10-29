# What is this?
## Helper utilities
from typing import TYPE_CHECKING, Any, Iterable, List, Literal, Optional, Union

import httpx

from remodl._logging import verbose_logger
from remodl.types.llms.openai import AllMessageValues

if TYPE_CHECKING:
    from opentelemetry.trace import Span as _Span

    from remodl.types.utils import ModelResponseStream

    Span = Union[_Span, Any]
else:
    Span = Any


def safe_divide_seconds(
    seconds: float, denominator: float, default: Optional[float] = None
) -> Optional[float]:
    """
    Safely divide seconds by denominator, handling zero division.

    Args:
        seconds: Time duration in seconds
        denominator: The divisor (e.g., number of tokens)
        default: Value to return if division by zero (defaults to None)

    Returns:
        The result of the division as a float (seconds per unit), or default if denominator is zero
    """
    if denominator <= 0:
        return default

    return float(seconds / denominator)


def safe_divide(
    numerator: Union[int, float], 
    denominator: Union[int, float], 
    default: Union[int, float] = 0
) -> Union[int, float]:
    """
    Safely divide two numbers, returning a default value if denominator is zero.
    
    Args:
        numerator: The number to divide
        denominator: The number to divide by
        default: Value to return if denominator is zero (defaults to 0)
    
    Returns:
        The result of numerator/denominator, or default if denominator is zero
    """
    if denominator == 0:
        return default
    return numerator / denominator


def map_finish_reason(
    finish_reason: str,
):  # openai supports 5 stop sequences - 'stop', 'length', 'function_call', 'content_filter', 'null'
    # anthropic mapping
    if finish_reason == "stop_sequence":
        return "stop"
    # cohere mapping - https://docs.cohere.com/reference/generate
    elif finish_reason == "COMPLETE":
        return "stop"
    elif finish_reason == "MAX_TOKENS":  # cohere + vertex ai
        return "length"
    elif finish_reason == "ERROR_TOXIC":
        return "content_filter"
    elif (
        finish_reason == "ERROR"
    ):  # openai currently doesn't support an 'error' finish reason
        return "stop"
    # huggingface mapping https://huggingface.github.io/text-generation-inference/#/Text%20Generation%20Inference/generate_stream
    elif finish_reason == "eos_token" or finish_reason == "stop_sequence":
        return "stop"
    elif (
        finish_reason == "FINISH_REASON_UNSPECIFIED" or finish_reason == "STOP"
    ):  # vertex ai - got from running `print(dir(response_obj.candidates[0].finish_reason))`: ['FINISH_REASON_UNSPECIFIED', 'MAX_TOKENS', 'OTHER', 'RECITATION', 'SAFETY', 'STOP',]
        return "stop"
    elif finish_reason == "SAFETY" or finish_reason == "RECITATION":  # vertex ai
        return "content_filter"
    elif finish_reason == "STOP":  # vertex ai
        return "stop"
    elif finish_reason == "end_turn" or finish_reason == "stop_sequence":  # anthropic
        return "stop"
    elif finish_reason == "max_tokens":  # anthropic
        return "length"
    elif finish_reason == "tool_use":  # anthropic
        return "tool_calls"
    elif finish_reason == "content_filtered":
        return "content_filter"
    return finish_reason


def remove_index_from_tool_calls(
    messages: Optional[List[AllMessageValues]],
):
    if messages is not None:
        for message in messages:
            _tool_calls = message.get("tool_calls")
            if _tool_calls is not None and isinstance(_tool_calls, list):
                for tool_call in _tool_calls:
                    if (
                        isinstance(tool_call, dict) and "index" in tool_call
                    ):  # Type guard to ensure it's a dict
                        tool_call.pop("index", None)

    return


def remove_items_at_indices(items: Optional[List[Any]], indices: Iterable[int]) -> None:
    """Remove items from a list in-place by index"""
    if items is None:
        return
    for index in sorted(set(indices), reverse=True):
        if 0 <= index < len(items):
            items.pop(index)


def add_missing_spend_metadata_to_remodl_metadata(
    remodl_metadata: dict, metadata: dict
) -> dict:
    """
    Helper to get remodl metadata for spend tracking

    PATCH for issue where both `remodl_metadata` and `metadata` are present in the kwargs
    and user_api_key values are in 'metadata'.
    """
    potential_spend_tracking_metadata_substring = "user_api_key"
    for key, value in metadata.items():
        if potential_spend_tracking_metadata_substring in key:
            remodl_metadata[key] = value
    return remodl_metadata


def get_metadata_variable_name_from_kwargs(
    kwargs: dict,
) -> Literal["metadata", "remodl_metadata"]:
    """
    Helper to return what the "metadata" field should be called in the request data

    - New endpoints return `remodl_metadata`
    - Old endpoints return `metadata`

    Context:
    - LiteLLM used `metadata` as an internal field for storing metadata
    - OpenAI then started using this field for their metadata
    - LiteLLM is now moving to using `remodl_metadata` for our metadata
    """
    return "remodl_metadata" if "remodl_metadata" in kwargs else "metadata"
    
def get_remodl_metadata_from_kwargs(kwargs: dict):
    """
    Helper to get remodl metadata from all remodl request kwargs

    Return `remodl_metadata` if it exists, otherwise return `metadata`
    """
    remodl_params = kwargs.get("remodl_params", {})
    if remodl_params:
        metadata = remodl_params.get("metadata", {})
        remodl_metadata = remodl_params.get("remodl_metadata", {})
        if remodl_metadata and metadata:
            remodl_metadata = add_missing_spend_metadata_to_remodl_metadata(
                remodl_metadata, metadata
            )
        if remodl_metadata:
            return remodl_metadata
        elif metadata:
            return metadata

    return {}


# Helper functions used for OTEL logging
def _get_parent_otel_span_from_kwargs(
    kwargs: Optional[dict] = None,
) -> Union[Span, None]:
    try:
        if kwargs is None:
            return None
        remodl_params = kwargs.get("remodl_params")
        _metadata = kwargs.get("metadata") or {}
        if "remodl_parent_otel_span" in _metadata:
            return _metadata["remodl_parent_otel_span"]
        elif (
            remodl_params is not None
            and remodl_params.get("metadata") is not None
            and "remodl_parent_otel_span" in remodl_params.get("metadata", {})
        ):
            return remodl_params["metadata"]["remodl_parent_otel_span"]
        elif "remodl_parent_otel_span" in kwargs:
            return kwargs["remodl_parent_otel_span"]
        return None
    except Exception as e:
        verbose_logger.exception(
            "Error in _get_parent_otel_span_from_kwargs: " + str(e)
        )
        return None


def process_response_headers(response_headers: Union[httpx.Headers, dict]) -> dict:
    from remodl.types.utils import OPENAI_RESPONSE_HEADERS

    openai_headers = {}
    processed_headers = {}
    additional_headers = {}

    for k, v in response_headers.items():
        if k in OPENAI_RESPONSE_HEADERS:  # return openai-compatible headers
            openai_headers[k] = v
        if k.startswith(
            "llm_provider-"
        ):  # return raw provider headers (incl. openai-compatible ones)
            processed_headers[k] = v
        else:
            additional_headers["{}-{}".format("llm_provider", k)] = v

    additional_headers = {
        **openai_headers,
        **processed_headers,
        **additional_headers,
    }
    return additional_headers


def preserve_upstream_non_openai_attributes(
    model_response: "ModelResponseStream", original_chunk: "ModelResponseStream"
):
    """
    Preserve non-OpenAI attributes from the original chunk.
    """
    expected_keys = set(model_response.model_fields.keys()).union({"usage"})
    for key, value in original_chunk.model_dump().items():
        if key not in expected_keys:
            setattr(model_response, key, value)


def safe_deep_copy(data):
    """
    Safe Deep Copy

    The LiteLLM request may contain objects that cannot be pickled/deep-copied
    (e.g., tracing spans, locks, clients). 
    
    This helper deep-copies each top-level key independently; on failure keeps
    original ref
    """
    import copy

    import remodl

    if remodl.safe_memory_mode is True:
        return data

    remodl_parent_otel_span: Optional[Any] = None
    # Step 1: Remove the remodl_parent_otel_span
    remodl_parent_otel_span = None
    if isinstance(data, dict):
        # remove remodl_parent_otel_span since this is not picklable
        if "metadata" in data and "remodl_parent_otel_span" in data["metadata"]:
            remodl_parent_otel_span = data["metadata"].pop("remodl_parent_otel_span")
            data["metadata"]["remodl_parent_otel_span"] = "placeholder"
        if (
            "remodl_metadata" in data
            and "remodl_parent_otel_span" in data["remodl_metadata"]
        ):
            remodl_parent_otel_span = data["remodl_metadata"].pop(
                "remodl_parent_otel_span"
            )
            data["remodl_metadata"]["remodl_parent_otel_span"] = "placeholder"

    # Step 2: Per-key deepcopy with fallback
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            try:
                new_data[k] = copy.deepcopy(v)
            except Exception:
                new_data[k] = v
    else:
        try:
            new_data = copy.deepcopy(data)
        except Exception:
            new_data = data

    # Step 3: re-add the remodl_parent_otel_span after doing a deep copy
    if isinstance(data, dict) and remodl_parent_otel_span is not None:
        if "metadata" in data and "remodl_parent_otel_span" in data["metadata"]:
            data["metadata"]["remodl_parent_otel_span"] = remodl_parent_otel_span
        if (
            "remodl_metadata" in data
            and "remodl_parent_otel_span" in data["remodl_metadata"]
        ):
            data["remodl_metadata"][
                "remodl_parent_otel_span"
            ] = remodl_parent_otel_span
    return new_data