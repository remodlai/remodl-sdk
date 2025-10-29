"""OpenAI Audio Transcription handler for Unified Guardrails."""

from remodl.llms.openai.transcriptions.guardrail_translation.handler import (
    OpenAIAudioTranscriptionHandler,
)
from remodl.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.transcription: OpenAIAudioTranscriptionHandler,
    CallTypes.atranscription: OpenAIAudioTranscriptionHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAIAudioTranscriptionHandler"]
