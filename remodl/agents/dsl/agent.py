"""
DSL for creating agents with fluent API.
"""

from typing import Any


class AgentBuilder:
    """
    Fluent builder for creating agents.
    
    Example:
        agent = create_agent(
            name="Foo Agent",
            role="You answer questions",
            tools=my_tools
        ).with_state(state, context, messages)
    """
    
    def __init__(self, name: str, role: str | None = None, tools: list | None = None):
        """
        Initialize agent builder.
        
        Args:
            name: Agent name
            role: Agent role/instructions
            tools: List of tools available to agent
        """
        self.name = name
        self.role = role
        self.tools = tools or []
        self._state = None
        self._context = None
        self._messages = None
    
    def with_state(self, state, context=None, messages=None):
        """
        Attach state configuration to the agent.
        
        Args:
            state: State schema or dict
            context: Optional context schema
            messages: Optional messages schema
            
        Returns:
            Self for chaining
        """
        self._state = state
        self._context = context
        self._messages = messages
        return self
    
    def with_tools(self, tools: list):
        """
        Add tools to the agent.
        
        Args:
            tools: List of tools
            
        Returns:
            Self for chaining
        """
        self.tools.extend(tools)
        return self
    
    def compile(self):
        """
        Compile the agent into an executable component.
        
        Returns:
            Compiled agent ready for use in workflow
        """
        # This will be implemented when we build the actual agent execution
        return CompiledAgent(
            name=self.name,
            role=self.role,
            tools=self.tools,
            state_schema=self._state,
            context_schema=self._context
        )
    
    def __repr__(self):
        return f"AgentBuilder(name={self.name}, role={self.role[:30] if self.role else None}...)"


class CompiledAgent:
    """Compiled agent ready for execution."""
    
    def __init__(self, name: str, role: str, tools: list, state_schema, context_schema):
        self.name = name
        self.role = role
        self.tools = tools
        self.state_schema = state_schema
        self.context_schema = context_schema
    
    def execute(self, state: dict) -> dict:
        """
        Execute the agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Placeholder - will be implemented with actual agent logic
        return state
    
    def to_dspy_component(self):
        """Convert to DSPy component for compilation."""
        # Placeholder
        return (f"{self.name}_agent", self)


def create_agent(
    name: str,
    role: str | None = None,
    tools: list | None = None
) -> AgentBuilder:
    """
    Create an agent with fluent API.
    
    Args:
        name: Agent name
        role: Agent role/instructions
        tools: List of tools available to agent
        
    Returns:
        AgentBuilder for fluent configuration
        
    Example:
        agent = create_agent(
            name="Search Agent",
            role="You search for information",
            tools=[search_tool, summarize_tool]
        ).with_state(state, context, messages)
    """
    return AgentBuilder(name=name, role=role, tools=tools)
