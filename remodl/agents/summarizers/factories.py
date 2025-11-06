"""
Factory functions for creating summarization strategies.
"""

from remodl.agents.summarizers.config import SummarizerConfig
import dspy


def default(
    last_n_msg: int = 3,
    max_summary_ratio: float = 0.75,
    keep_media: bool = True,
    offload_media: bool = True
) -> SummarizerConfig:
    """
    Default conversational summarization.
    Maintains natural conversation flow.
    
    Args:
        last_n_msg: Number of recent messages to keep verbatim
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
        offload_media: Whether to offload base64 to storage
    """
    return SummarizerConfig(
        name="default",
        max_ratio=max_summary_ratio,
        approach="conversation_flow",
        prioritize="user_intent",
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=offload_media
    )


def chrono(
    last_n_msg: int = 4,
    max_summary_ratio: float = 0.20,
    keep_media: bool = True,
    offload_media: bool = True
) -> SummarizerConfig:
    """
    Chronological summarization.
    Maintains strict timeline of events.
    Aggressive summarization (low ratio).
    
    Args:
        last_n_msg: Number of recent messages to keep verbatim
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
        offload_media: Whether to offload base64 to storage
    """
    return SummarizerConfig(
        name="chrono",
        max_ratio=max_summary_ratio,
        approach="chronological",
        prioritize="timeline_events",
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=offload_media
    )


def adaptive(
    last_n_msg: int = 5,
    instruct: str = "Analyze the conversation and prioritize key context",
    max_summary_ratio: float = 0.75,
    keep_media: bool = True,
    offload_media: bool = True
) -> SummarizerConfig:
    """
    Adaptive summarization with custom instructions.
    Uses LLM to intelligently decide what to keep.
    
    Args:
        last_n_msg: Number of recent messages to keep verbatim
        instruct: Custom instructions for the summarizer
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
        offload_media: Whether to offload base64 to storage
    """
    return SummarizerConfig(
        name="adaptive",
        max_ratio=max_summary_ratio,
        approach="adaptive",
        prioritize="llm_determined",
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=offload_media,
        custom_instructions=instruct
    )


def custom(
    name: str,
    approach: str,
    prioritize: str,
    last_n_msg: int = 3,
    max_summary_ratio: float = 0.75,
    keep_media: bool = True,
    offload_media: bool = True,
    instruct: str | None = None,
    signature: type[dspy.Signature] | None = None
) -> SummarizerConfig:
    """
    Fully custom summarization strategy.
    
    Args:
        name: Name for this strategy
        approach: Summarization approach (e.g., "key_facts", "action_items")
        prioritize: What to prioritize (e.g., "decisions_made", "user_preferences")
        last_n_msg: Number of recent messages to keep verbatim
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
        offload_media: Whether to offload base64 to storage
        instruct: Optional custom instructions
        signature: Optional custom DSPy signature
    """
    return SummarizerConfig(
        name=name,
        max_ratio=max_summary_ratio,
        approach=approach,
        prioritize=prioritize,
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=offload_media,
        custom_instructions=instruct,
        signature=signature
    )


def aggressive(
    last_n_msg: int = 2,
    max_summary_ratio: float = 0.50,
    keep_media: bool = False
) -> SummarizerConfig:
    """
    Aggressive summarization for minimal context.
    Good for cost optimization.
    
    Args:
        last_n_msg: Number of recent messages to keep verbatim
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
    """
    return SummarizerConfig(
        name="aggressive",
        max_ratio=max_summary_ratio,
        approach="key_facts",
        prioritize="critical_info_only",
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=True
    )


def conservative(
    last_n_msg: int = 10,
    max_summary_ratio: float = 0.90,
    keep_media: bool = True
) -> SummarizerConfig:
    """
    Conservative summarization - keeps more context.
    Good for complex reasoning tasks.
    
    Args:
        last_n_msg: Number of recent messages to keep verbatim
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
    """
    return SummarizerConfig(
        name="conservative",
        max_ratio=max_summary_ratio,
        approach="detailed_summary",
        prioritize="comprehensive_context",
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=False
    )


def production(
    last_n_msg: int = 5,
    max_summary_ratio: float = 0.70,
    keep_media: bool = True,
    offload_media: bool = True
) -> SummarizerConfig:
    """
    Production-ready summarization.
    Balanced approach for deployed systems.
    
    Args:
        last_n_msg: Number of recent messages to keep verbatim
        max_summary_ratio: Ratio (0.0-1.0) of context before summarizing
        keep_media: Whether to keep media references
        offload_media: Whether to offload base64 to storage
    """
    return SummarizerConfig(
        name="production",
        max_ratio=max_summary_ratio,
        approach="conversation_flow",
        prioritize="action_items",
        keep_messages=last_n_msg,
        keep_media=keep_media,
        offload_media=offload_media
    )


def none() -> None:
    """
    No summarization.
    Good for development/debugging.
    
    Returns:
        None
    """
    return None
