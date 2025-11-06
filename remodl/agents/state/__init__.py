"""
State management for agent workflows.

Provides decorators for state initialization and field reducers.
"""

from remodl.agents.state.decorators import chat_state, messages, context, memory
from remodl.agents.state.reducers import append_reducer, replace_reducer, merge_dict_reducer
from remodl.agents.state.context import (
    calc_current_context_window,
    get_context_ratio,
    context_window
)

__all__ = [
    "chat_state",
    "messages",
    "context",
    "memory",
    "append_reducer",
    "replace_reducer",
    "merge_dict_reducer",
    "calc_current_context_window",
    "get_context_ratio",
    "context_window",
]
