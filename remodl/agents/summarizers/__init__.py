"""
Summarization strategies for context management.

Provides factory functions for different summarization approaches.
"""

from remodl.agents.summarizers.factories import (
    default,
    chrono,
    adaptive,
    custom,
    aggressive,
    conservative,
    production,
    none
)

from remodl.agents.summarizers.config import SummarizerConfig
from remodl.agents.summarizers.strategies import SummaryStrategy, MediaSummary, SummaryStruct

__all__ = [
    # Factory functions
    "default",
    "chrono",
    "adaptive",
    "custom",
    "aggressive",
    "conservative",
    "production",
    "none",
    
    # Config
    "SummarizerConfig",
    
    # Strategies
    "SummaryStrategy",
    "MediaSummary",
    "SummaryStruct",
]
