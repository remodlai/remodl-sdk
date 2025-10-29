"""Cohere Rerank handler for Unified Guardrails."""

from remodl.llms.cohere.rerank.guardrail_translation.handler import CohereRerankHandler
from remodl.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.rerank: CohereRerankHandler,
    CallTypes.arerank: CohereRerankHandler,
}

__all__ = ["guardrail_translation_mappings", "CohereRerankHandler"]
