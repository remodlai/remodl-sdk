"""
DSL for creating routers with fluent API.
"""


class AgenticRouterBuilder:
    """
    Builder for agentic routers (LLM-based routing).
    
    Example:
        router = agentic_router.create(name="duck router", has_rules=True)
        router.add_rule("when question is duck related tag as 'duck', else 'not_duck'")
        router.init()
    """
    
    def __init__(self, name: str, has_rules: bool = False):
        """
        Initialize router builder.
        
        Args:
            name: Router name
            has_rules: Whether this router uses explicit rules
        """
        self.name = name
        self.has_rules = has_rules
        self.rules = []
    
    def add_rule(self, rule: str):
        """
        Add a routing rule.
        
        Args:
            rule: Routing rule as string
            
        Returns:
            Self for chaining
        """
        self.rules.append(rule)
        return self
    
    def init(self):
        """
        Initialize and compile the router.
        
        Returns:
            Compiled router ready for use
        """
        return CompiledRouter(
            name=self.name,
            rules=self.rules,
            mode="agentic"
        )
    
    def __repr__(self):
        return f"AgenticRouterBuilder(name={self.name}, rules={len(self.rules)})"


class CompiledRouter:
    """Compiled router ready for execution."""
    
    def __init__(self, name: str, rules: list[str], mode: str):
        self.name = name
        self.rules = rules
        self.mode = mode
    
    def route(self, state: dict) -> str:
        """
        Route based on state.
        
        Args:
            state: Current state
            
        Returns:
            Next node name
        """
        # Placeholder - will be implemented with actual routing logic
        return "next_node"
    
    def to_dspy_component(self):
        """Convert to DSPy component for compilation."""
        # Placeholder
        return (f"{self.name}_router", self)


class AgenticRouterFactory:
    """Factory for creating agentic routers."""
    
    def create(self, name: str, has_rules: bool = False) -> AgenticRouterBuilder:
        """
        Create a new agentic router.
        
        Args:
            name: Router name
            has_rules: Whether this router uses explicit rules
            
        Returns:
            AgenticRouterBuilder for configuration
        """
        return AgenticRouterBuilder(name=name, has_rules=has_rules)


# Global factory instance
agentic_router = AgenticRouterFactory()
