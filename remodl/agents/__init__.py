"""
Remodl Agents Framework

A composable, DSPy-native agent framework with state management,
automatic summarization, and agent-to-agent communication.
"""

# DSL exports
from remodl.agents.dsl.agent import create_agent
from remodl.agents.dsl.router import agentic_router
from remodl.agents.dsl.tools import mcptool
from remodl.agents.dsl.factories import workflow, start, end

# State management
from remodl.agents.state.decorators import chat_state, messages, context, memory

# Summarizers
from remodl.agents import summarizers

# Core types
from remodl.agents.workflow.builder import WorkflowBuilder
from remodl.agents.workflow.compiler import CompiledWorkflow

__version__ = "0.1.0"

__all__ = [
    # DSL
    "create_agent",
    "agentic_router",
    "mcptool",
    "workflow",
    "start",
    "end",
    
    # State
    "chat_state",
    "messages",
    "context",
    "memory",
    
    # Summarizers
    "summarizers",
    
    # Core
    "WorkflowBuilder",
    "CompiledWorkflow",
]
