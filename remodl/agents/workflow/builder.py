"""
Fluent builder for creating workflows.
"""

from typing import Any
from remodl.agents.summarizers.config import SummarizerConfig
from remodl.agents.workflow.compiler import CompiledWorkflow


class WorkflowBuilder:
    """
    Fluent builder for agent workflows.
    
    Example:
        workflow = WorkflowBuilder(name="MyWorkflow")
        workflow.starts_at(start_node)
        workflow.layer(1, router)
        workflow.layer(2, [agent_a, agent_b])
        compiled = workflow.compile(summarizer="adaptive")
    """
    
    def __init__(
        self,
        name: str,
        streaming: bool = False,
        iterations_max: int = 10,
        model: str | None = None
    ):
        """
        Initialize workflow builder.
        
        Args:
            name: Workflow name
            streaming: Enable streaming mode
            iterations_max: Maximum iterations
            model: Default model to use
        """
        self.name = name
        self.streaming = streaming
        self.iterations_max = iterations_max
        self.model = model
        self.layers: dict[int, list] = {}
        self.start_node = None
        self.end_node = None
    
    def starts_at(self, node):
        """
        Define the starting node.
        
        Args:
            node: Starting node
            
        Returns:
            Self for chaining
        """
        self.start_node = node
        return self
    
    def layer(self, layer_num: int, nodes):
        """
        Define a layer of nodes.
        
        Args:
            layer_num: Layer number (execution order)
            nodes: Single node or list of nodes
            
        Returns:
            Self for chaining
        """
        if not isinstance(nodes, list):
            nodes = [nodes]
        self.layers[layer_num] = nodes
        return self
    
    def ends_at(self, node):
        """
        Define the ending node.
        
        Args:
            node: Ending node
            
        Returns:
            Self for chaining
        """
        self.end_node = node
        return self
    
    def compile(
        self,
        summarizer: str | SummarizerConfig | None = "default"
    ) -> CompiledWorkflow:
        """
        Compile the workflow into an executable DSPy Module.
        
        Args:
            summarizer: Summarization strategy:
                - None: No summarization
                - "default", "aggressive", etc: Named preset
                - SummarizerConfig: Custom configuration
                
        Returns:
            Compiled workflow ready for execution
        """
        from remodl.agents.summarizers.factories import (
            default, aggressive, conservative, production
        )
        
        # Resolve summarizer config
        if summarizer is None:
            summarizer_config = None
        elif isinstance(summarizer, str):
            # Named summarizers
            named_summarizers = {
                "default": default(),
                "aggressive": aggressive(),
                "conservative": conservative(),
                "production": production(),
            }
            
            if summarizer not in named_summarizers:
                raise ValueError(
                    f"Unknown summarizer: {summarizer}. "
                    f"Available: {list(named_summarizers.keys())}"
                )
            summarizer_config = named_summarizers[summarizer]
        elif isinstance(summarizer, SummarizerConfig):
            summarizer_config = summarizer
        else:
            raise ValueError(f"Invalid summarizer type: {type(summarizer)}")
        
        # Create compiled workflow
        workflow = CompiledWorkflow(
            name=self.name,
            start_node=self.start_node,
            layers=self.layers,
            end_node=self.end_node,
            streaming=self.streaming,
            iterations_max=self.iterations_max,
            model=self.model,
            summarizer_config=summarizer_config
        )
        
        # Generate the DSPy module
        workflow.compile()
        
        return workflow
