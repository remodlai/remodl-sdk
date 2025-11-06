"""
Compiles workflows into executable DSPy modules.
"""

from typing import Any
import dspy
import cloudpickle

from remodl.agents.summarizers.config import SummarizerConfig
from remodl.agents.summarizers.strategies import SummaryStrategy


class CompiledWorkflow:
    """
    Compiled workflow that executes as a DSPy Module.
    
    The workflow is converted to a DSPy Module at compile time,
    allowing it to be optimized, serialized, and deployed.
    """
    
    def __init__(
        self,
        name: str,
        start_node,
        layers: dict,
        end_node,
        streaming: bool,
        iterations_max: int,
        model: str | None,
        summarizer_config: SummarizerConfig | None
    ):
        """Initialize compiled workflow."""
        self.name = name
        self.start_node = start_node
        self.layers = layers
        self.end_node = end_node
        self.streaming = streaming
        self.iterations_max = iterations_max
        self.model = model
        self.summarizer_config = summarizer_config
        self._dspy_module = None
        
        # Initialize summarizer if configured
        if summarizer_config:
            if summarizer_config.signature:
                self.summarizer = dspy.ChainOfThought(summarizer_config.signature)
            else:
                self.summarizer = dspy.ChainOfThought(SummaryStrategy)
    
    def compile(self) -> dspy.Module:
        """
        Generate DSPy Module from workflow definition.
        
        Returns:
            Compiled DSPy Module
        """
        # Collect all DSPy components from nodes
        components = {}
        for layer_num, nodes in self.layers.items():
            for node in nodes:
                if hasattr(node, 'to_dspy_component'):
                    comp_name, component = node.to_dspy_component()
                    components[comp_name] = component
        
        # Add summarizer
        if self.summarizer_config:
            components['summarizer'] = self.summarizer
            components['summarizer_config'] = self.summarizer_config
        
        # Generate the module class
        module_class = self._generate_module_class(components)
        self._dspy_module = module_class()
        
        print(f"✅ [Compile] Generated DSPy Module: {self.name}Module")
        if self.summarizer_config:
            print(f"   Summarizer: {self.summarizer_config.name}")
            print(f"   Max Ratio: {self.summarizer_config.max_ratio:.0%}")
            print(f"   Approach: {self.summarizer_config.approach}")
            print(f"   Keep Messages: {self.summarizer_config.keep_messages}")
        
        return self._dspy_module
    
    def _generate_module_class(self, components: dict) -> type[dspy.Module]:
        """
        Dynamically generate DSPy Module class.
        
        Args:
            components: Dictionary of component name -> component
            
        Returns:
            Generated DSPy Module class
        """
        class_name = f"{self.name.replace(' ', '')}Module"
        
        # Build module code
        module_code = self._build_module_code(class_name, components)
        
        # Execute to create class
        namespace = {
            'dspy': dspy,
            'components': components,
            'layers': self.layers
        }
        exec(module_code, namespace)
        
        return namespace[class_name]
    
    def _build_module_code(self, class_name: str, components: dict) -> str:
        """Build the Python code for the module class."""
        code = f"class {class_name}(dspy.Module):\n"
        code += "    def __init__(self):\n"
        code += "        super().__init__()\n"
        
        # Add components
        for comp_name in components:
            code += f"        self.{comp_name} = components['{comp_name}']\n"
        
        # Add forward method
        code += self._build_forward_method()
        
        # Add helper methods
        code += self._build_helper_methods()
        
        return code
    
    def _build_forward_method(self) -> str:
        """Build the forward() method code."""
        code = """
    def forward(self, **kwargs):
        '''Execute workflow with state management and summarization'''
        state = kwargs
        
        # Ensure state structure
        if 'messages' not in state:
            state['messages'] = []
        if 'context' not in state:
            state['context'] = {}
        if 'memory' not in state:
            state['memory'] = {}
        
        # Initial summarization check
        if hasattr(self, 'summarizer_config') and self.summarizer_config:
            state = self._maybe_summarize(state, "initial")
        
        # Execute layers
"""
        
        for layer_num in sorted(self.layers.keys()):
            code += f"""
        # Layer {layer_num}
        state = self._execute_layer_{layer_num}(state)
        if hasattr(self, 'summarizer_config') and self.summarizer_config:
            state = self._maybe_summarize(state, "layer_{layer_num}")
"""
        
        code += """
        return dspy.Prediction(**state)
"""
        return code
    
    def _build_helper_methods(self) -> str:
        """Build helper methods like _maybe_summarize."""
        return """
    def _maybe_summarize(self, state, checkpoint):
        '''Apply summarization if needed'''
        if not hasattr(self, 'summarizer_config'):
            return state
        
        config = self.summarizer_config
        ratio = self._get_context_ratio(state)
        
        if ratio > config.max_ratio:
            print(f"[Summarize @ {checkpoint}] Context at {ratio:.1%} exceeds {config.max_ratio:.1%}")
            
            # Run summarization
            result = self.summarizer(
                approach=config.approach,
                prioritize=config.prioritize,
                keep_messages=config.keep_messages,
                keep_media=config.keep_media,
                offload_media=config.offload_media,
                messages=state.get('messages', []),
                context=state.get('context', {}),
                memory=state.get('memory', {})
            )
            
            summary = result.summary
            
            # Create summary message
            summary_message = {
                'role': 'system',
                'content': summary.summary,
                'type': 'summary',
                'checkpoint': checkpoint
            }
            
            # Update state
            state = state.copy()
            state['messages'] = [summary_message] + summary.messages[-config.keep_messages:]
            
            new_ratio = self._get_context_ratio(state)
            saved = int((ratio - new_ratio) * 128000)
            print(f"[Summarize] Reduced to {new_ratio:.1%} (saved ~{saved:,} tokens)")
        
        return state
    
    def _get_context_ratio(self, state):
        '''Calculate context usage ratio'''
        total_tokens = 0
        for msg in state.get('messages', []):
            content = msg.get('content', '')
            if isinstance(content, str):
                total_tokens += len(content) // 4
            elif isinstance(content, list):
                total_tokens += len(str(content)) // 4
        total_tokens += len(str(state.get('context', {}))) // 4
        total_tokens += len(str(state.get('memory', {}))) // 4
        return total_tokens / 128000
    
    def _execute_layer_1(self, state):
        '''Placeholder for layer execution'''
        return state
"""
    
    def save(self, path: str):
        """
        Save compiled module using cloudpickle.
        
        Args:
            path: File path to save to
        """
        if not self._dspy_module:
            raise ValueError("Must compile() before saving")
        
        with open(path, 'wb') as f:
            cloudpickle.dump(self._dspy_module, f)
        
        print(f"💾 [Save] Workflow saved to {path}")
    
    @staticmethod
    def load(path: str) -> dspy.Module:
        """
        Load a compiled module.
        
        Args:
            path: File path to load from
            
        Returns:
            Loaded DSPy Module
        """
        with open(path, 'rb') as f:
            module = cloudpickle.load(f)
        
        print(f"📂 [Load] Workflow loaded from {path}")
        return module
    
    def optimize(self, trainset, metric, optimizer: str = "mipro"):
        """
        Optimize the workflow using DSPy optimizers.
        
        Args:
            trainset: Training dataset
            metric: Evaluation metric
            optimizer: Optimizer name ("mipro", "bootstrap", etc.)
            
        Returns:
            Self for chaining
        """
        if not self._dspy_module:
            raise ValueError("Must compile() before optimizing")
        
        if optimizer == "mipro":
            from dspy.teleprompt import MIPRO
            teleprompter = MIPRO(metric=metric, num_candidates=10)
        elif optimizer == "bootstrap":
            from dspy.teleprompt import BootstrapFewShot
            teleprompter = BootstrapFewShot(metric=metric)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer}")
        
        # Optimize
        self._dspy_module = teleprompter.compile(
            self._dspy_module,
            trainset=trainset
        )
        
        print(f"🎯 [Optimize] Workflow optimized using {optimizer}")
        return self
    
    def __call__(self, **kwargs):
        """Execute the compiled workflow."""
        if not self._dspy_module:
            raise ValueError("Must compile() before execution")
        
        return self._dspy_module(**kwargs)
    
    def activateA2A(self):
        """
        Activate Agent-to-Agent communication.
        
        Returns:
            A2A coordinator
        """
        from remodl.agents.a2a.coordinator import A2ACoordinator
        
        coordinator = A2ACoordinator(self)
        coordinator.activate()
        
        return coordinator
