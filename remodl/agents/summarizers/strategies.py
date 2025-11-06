"""
DSPy signatures and Pydantic models for summarization.
"""

from pydantic import BaseModel, Field
import dspy


class MediaSummary(BaseModel):
    """Summary of media content that was offloaded."""
    
    name: str = Field(description="The name of the media file")
    summary: str = Field(description="A short summary of what the media is")
    location: str = Field(description="The URL of the uploaded media")


class SummaryStruct(BaseModel):
    """Structured output from summarization."""
    
    summary: str = Field(description="The summary to max length")
    media: list[MediaSummary] = Field(description="The media offload", default_factory=list)
    messages: list = Field(description="The kept messages", default_factory=list)
    memories: list = Field(description="The kept memories", default_factory=list)


class SummaryStrategy(dspy.Signature):
    """
    Summarize the current state of the session.
    
    You will receive:
    - approach: The overall summarization strategy
    - prioritize: What information to prioritize in the summary
    - keep_messages: Number of most recent messages to maintain verbatim
    - keep_media: Whether to keep any active media in the summarized content
    - offload_media: Whether to offload any base64 media to cold storage
    """
    
    # Strategy parameters
    approach: str = dspy.InputField(
        desc="Summarization strategy (e.g., 'conversation_flow', 'key_facts', 'chronological')"
    )
    prioritize: str = dspy.InputField(
        desc="What to prioritize (e.g., 'user_intent', 'decisions_made', 'action_items')"
    )
    keep_messages: int = dspy.InputField(
        desc="Number of recent messages to keep verbatim"
    )
    keep_media: bool = dspy.InputField(
        desc="Whether to keep active media"
    )
    offload_media: bool = dspy.InputField(
        desc="Whether to offload base64 media to cold storage"
    )
    
    # Current state
    messages: list = dspy.InputField(desc="Current message history")
    context: dict = dspy.InputField(desc="Current context")
    memory: dict = dspy.InputField(desc="Current memory state")
    
    # Output
    summary: SummaryStruct = dspy.OutputField(desc="Structured summary result")
