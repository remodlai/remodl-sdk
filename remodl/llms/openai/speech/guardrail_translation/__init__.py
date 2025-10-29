"""OpenAI Text-to-Speech handler for Unified Guardrails."""

from remodl.llms.openai.speech.guardrail_translation.handler import (
    OpenAITextToSpeechHandler,
)
from remodl.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.speech: OpenAITextToSpeechHandler,
    CallTypes.aspeech: OpenAITextToSpeechHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAITextToSpeechHandler"]
