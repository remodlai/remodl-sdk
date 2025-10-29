"""OpenAI Responses API handler for Unified Guardrails."""

from remodl.llms.openai.responses.guardrail_translation.handler import (
    OpenAIResponsesHandler,
)
from remodl.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.responses: OpenAIResponsesHandler,
    CallTypes.aresponses: OpenAIResponsesHandler,
}
__all__ = ["guardrail_translation_mappings"]
