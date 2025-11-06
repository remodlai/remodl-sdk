"""
Domain Specific Language (DSL) for building agent workflows.

Provides a clean, fluent API for composing agents and workflows.
"""

from remodl.agents.dsl.agent import create_agent, AgentBuilder
from remodl.agents.dsl.router import agentic_router, AgenticRouterFactory
from remodl.agents.dsl.tools import mcptool, MCPToolWrapper
from remodl.agents.dsl.factories import workflow, start, end

__all__ = [
    "create_agent",
    "AgentBuilder",
    "agentic_router",
    "mcptool",
    "workflow",
    "start",
    "end",
]
