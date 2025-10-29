"""OpenAI Text Completion handler for Unified Guardrails."""

from remodl.llms.openai.completion.guardrail_translation.handler import (
    OpenAITextCompletionHandler,
)
from remodl.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.text_completion: OpenAITextCompletionHandler,
    CallTypes.atext_completion: OpenAITextCompletionHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAITextCompletionHandler"]
