"""
Factory objects for creating workflow components.
"""

from remodl.agents.workflow.builder import WorkflowBuilder
from remodl.agents.workflow.nodes import CompiledStartNode, CompiledEndNode


class WorkflowFactory:
    """Factory for creating workflows with fluent API."""
    
    def create(
        self,
        name: str,
        streaming: bool = False,
        iterations_max: int = 10,
        model: str | None = None
    ) -> WorkflowBuilder:
        """
        Create a new workflow builder.
        
        Args:
            name: Workflow name
            streaming: Enable streaming mode
            iterations_max: Maximum iterations
            model: Default model to use
            
        Returns:
            WorkflowBuilder instance
            
        Example:
            dw = workflow.create(
                name='duck workflow',
                streaming=True,
                iterations_max=3,
                model='remodlai/nova-chat-3b'
            )
        """
        return WorkflowBuilder(
            name=name,
            streaming=streaming,
            iterations_max=iterations_max,
            model=model
        )


class StartNodeFactory:
    """Factory for creating start nodes."""
    
    def init(self, expects: list[str]) -> CompiledStartNode:
        """
        Create a start node with expected inputs.
        
        Args:
            expects: List of expected input field names
            
        Returns:
            Compiled start node
            
        Example:
            start_node = start.init(expects=["messages", "query", "session"])
        """
        return CompiledStartNode(expects=expects)


class EndNodeFactory:
    """Factory for creating end nodes."""
    
    def init(self, expects: list[str]) -> CompiledEndNode:
        """
        Create an end node with expected outputs.
        
        Args:
            expects: List of expected output field names
            
        Returns:
            Compiled end node
            
        Example:
            end_node = end.init(expects=["answer", "confidence"])
        """
        return CompiledEndNode(expects=expects)


# Global factory instances
workflow = WorkflowFactory()
start = StartNodeFactory()
end = EndNodeFactory()
