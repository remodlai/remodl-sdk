"""
Configuration model for summarization strategies.
"""

from pydantic import BaseModel, Field
from typing import Literal
import dspy


class SummarizerConfig(BaseModel):
    """
    Configuration for a summarization strategy.
    
    Attributes:
        name: Strategy name
        max_ratio: Context ratio (0.0-1.0) that triggers summarization
        approach: Summarization approach (e.g., "conversation_flow", "chronological")
        prioritize: What to prioritize in summary
        keep_messages: Number of recent messages to keep verbatim
        keep_media: Whether to preserve media references
        offload_media: Whether to offload base64 media to storage
        custom_instructions: Optional custom instructions for the summarizer
        signature: Optional custom DSPy signature for summarization
    """
    
    name: str
    max_ratio: float = Field(default=0.75, ge=0.0, le=1.0)
    approach: str
    prioritize: str
    keep_messages: int = Field(default=3, ge=0)
    keep_media: bool = True
    offload_media: bool = True
    custom_instructions: str | None = None
    signature: type[dspy.Signature] | None = None
    
    class Config:
        arbitrary_types_allowed = True
