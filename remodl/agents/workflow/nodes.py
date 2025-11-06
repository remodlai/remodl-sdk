"""
Special workflow nodes for graph entry and exit points.
"""

from typing import Any


class StartNode:
    """
    Starting node for a workflow.
    Validates expected inputs.
    """
    
    def __init__(self, expects: list[str]):
        """
        Initialize start node.
        
        Args:
            expects: List of expected input field names
        """
        self.expects = expects
    
    def process(self, state: dict) -> dict:
        """
        Process the input state, validating expected fields.
        
        Args:
            state: Input state
            
        Returns:
            Validated state
        """
        # Validate expected fields
        missing = [field for field in self.expects if field not in state]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return state
    
    def __repr__(self):
        return f"StartNode(expects={self.expects})"


class EndNode:
    """
    Ending node for a workflow.
    Formats final output.
    """
    
    def __init__(self, expects: list[str]):
        """
        Initialize end node.
        
        Args:
            expects: List of expected output field names
        """
        self.expects = expects
    
    def process(self, state: dict) -> dict:
        """
        Process the final state, extracting expected outputs.
        
        Args:
            state: Final state
            
        Returns:
            Formatted output state
        """
        # Extract only expected fields if specified
        if self.expects:
            return {k: v for k, v in state.items() if k in self.expects}
        
        return state
    
    def __repr__(self):
        return f"EndNode(expects={self.expects})"


class CompiledStartNode:
    """Compiled start node ready for use in workflow."""
    
    def __init__(self, expects: list[str]):
        self.node = StartNode(expects)
        self.expects = expects


class CompiledEndNode:
    """Compiled end node ready for use in workflow."""
    
    def __init__(self, expects: list[str]):
        self.node = EndNode(expects)
        self.expects = expects
