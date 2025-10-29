from remodl._uuid import uuid
from typing import Optional

import remodl
from remodl._logging import verbose_logger
from remodl.remodl_core_utils.core_helpers import safe_deep_copy

from .asyncify import run_async_function


async def async_completion_with_fallbacks(**kwargs):
    """
    Asynchronously attempts completion with fallback models if the primary model fails.

    Args:
        **kwargs: Keyword arguments for completion, including:
            - model (str): Primary model to use
            - fallbacks (List[Union[str, dict]]): List of fallback models/configs
            - Other completion parameters

    Returns:
        ModelResponse: The completion response from the first successful model

    Raises:
        Exception: If all models fail and no response is generated
    """
    # Extract and prepare parameters
    nested_kwargs = kwargs.pop("kwargs", {})
    original_model = kwargs["model"]
    model = original_model
    fallbacks = [original_model] + nested_kwargs.pop("fallbacks", [])
    kwargs.pop("acompletion", None)  # Remove to prevent keyword conflicts
    remodl_call_id = str(uuid.uuid4())
    base_kwargs = {**kwargs, **nested_kwargs, "remodl_call_id": remodl_call_id}

    # fields to remove
    base_kwargs.pop("model", None)  # Remove model as it will be set per fallback
    remodl_logging_obj = base_kwargs.pop("remodl_logging_obj", None)

    # Try each fallback model
    most_recent_exception_str: Optional[str] = None
    for fallback in fallbacks:
        try:
            completion_kwargs = safe_deep_copy(base_kwargs)
            # Handle dictionary fallback configurations
            if isinstance(fallback, dict):
                model = fallback.pop("model", original_model)
                completion_kwargs.update(fallback)
            else:
                model = fallback

            response = await remodl.acompletion(
                **completion_kwargs,
                model=model,
                remodl_logging_obj=remodl_logging_obj,
            )

            if response is not None:
                return response

        except Exception as e:
            verbose_logger.exception(
                f"Fallback attempt failed for model {model}: {str(e)}"
            )
            most_recent_exception_str = str(e)
            continue

    raise Exception(
        f"{most_recent_exception_str}. All fallback attempts failed. Enable verbose logging with `remodl.set_verbose=True` for details."
    )


def completion_with_fallbacks(**kwargs):
    return run_async_function(async_function=async_completion_with_fallbacks, **kwargs)
