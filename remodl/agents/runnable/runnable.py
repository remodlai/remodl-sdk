from typing import TypeVar, Generic, Any, Callable
from pydantic import BaseModel
from abc import ABC, abstractmethod
from remodl import dspy

# TypeVars
StateT = TypeVar("StateT", bound=dict)
ContextT = TypeVar("ContextT", bound=dict | None)
OutputT = TypeVar("OutputT", bound=dict)


# ============= LAYER 1: BASE CONTRACT =============

class RunnableBase(BaseModel, Generic[StateT, ContextT, OutputT], ABC):
    """
    Pure contract: Input → Output
    This is what gets compiled into part of a DSPy Module
    """
    name: str
    expects: dict[str, Any]
    returns: dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """The actual logic - this becomes part of the DSPy Module's forward()"""
        pass

    @abstractmethod
    def to_dspy_component(self) -> tuple[str, Any]:
        """
        Convert this runnable to DSPy component(s).
        Returns: (component_name, component_instance)

        This is called during compile() to generate the DSPy Module.
        """
        pass


# ============= LAYER 2: COMMON UTILITIES =============

class Runnable(RunnableBase[StateT, ContextT, OutputT]):
    """
    Adds common utilities like LangChain's Runnable.
    Still abstract - subclasses implement forward() and to_dspy_component()
    """

    def __call__(self, state: StateT, context: ContextT = None) -> OutputT:
        """Invoke during runtime"""
        return self.forward(state, context)

    def invoke(self, state: StateT, context: ContextT = None) -> OutputT:
        """Explicit invoke"""
        return self.forward(state, context)

    def batch(self, states: list[StateT], context: ContextT = None) -> list[OutputT]:
        """Batch execution"""
        return [self.forward(state, context) for state in states]

    def pipe(self, next_runnable: "Runnable") -> "RunnableSequence":
        """Chain runnables - becomes a sequence in the DSPy Module"""
        return RunnableSequence(runnables=[self, next_runnable])

    def generate_forward_code(self) -> str:
        """
        Generate the forward() method code for this runnable.
        Used during compile() to build the DSPy Module.
        """
        return f"""
        # Execute {self.name}
        state = self._{self.name.replace(' ', '_').lower()}(state, context)
"""

    @abstractmethod
    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Override in subclasses"""
        pass

    @abstractmethod
    def to_dspy_component(self) -> tuple[str, Any]:
        """Override in subclasses"""
        pass


# ============= LAYER 3: SPECIFIC IMPLEMENTATIONS =============

class SignatureRunnable(Runnable[StateT, ContextT, OutputT]):
    """
    Executes a DSPy Signature.
    Compiles to: dspy.Predict or dspy.ChainOfThought
    """

    signature: type[dspy.Signature]
    use_cot: bool = False
    _predictor: Any = None

    def model_post_init(self, __context):
        """Initialize the predictor"""
        if self.use_cot:
            self._predictor = dspy.ChainOfThought(self.signature)
        else:
            self._predictor = dspy.Predict(self.signature)

    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Execute the signature"""
        inputs = {k: state[k] for k in self.expects.keys() if k in state}
        result = self._predictor(**inputs)

        output = {}
        for return_key in self.returns.keys():
            if hasattr(result, return_key):
                output[return_key] = getattr(result, return_key)

        return output

    def to_dspy_component(self) -> tuple[str, Any]:
        """
        Returns the DSPy predictor to be included in the compiled module.
        """
        component_name = f"{self.name.replace(' ', '_').lower()}_predictor"
        return (component_name, self._predictor)


class ModuleRunnable(Runnable[StateT, ContextT, OutputT]):
    """
    Executes a custom DSPy Module.
    Compiles to: the DSPy Module instance
    """

    module: dspy.Module

    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Execute the module"""
        inputs = {k: state[k] for k in self.expects.keys() if k in state}
        result = self.module(**inputs)

        if isinstance(result, dict):
            return result
        elif isinstance(result, dspy.Prediction):
            return result.model_dump()
        else:
            return {k: getattr(result, k) for k in self.returns.keys() 
                   if hasattr(result, k)}

    def to_dspy_component(self) -> tuple[str, Any]:
        """Returns the module instance"""
        component_name = f"{self.name.replace(' ', '_').lower()}_module"
        return (component_name, self.module)


class ConditionalRunnable(Runnable[StateT, ContextT, OutputT]):
    """
    Logic gating - if/else branching.
    Compiles to: conditional logic in the DSPy Module's forward()
    """

    condition_fn: Callable[[StateT, ContextT], bool]
    true_branch: str
    false_branch: str

    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Evaluate condition"""
        result = self.condition_fn(state, context)
        return {
            "next_node": self.true_branch if result else self.false_branch,
            "condition_result": result,
            **state
        }

    def to_dspy_component(self) -> tuple[str, Any]:
        """
        Conditionals don't become components - they become control flow.
        Return None to signal this is control flow logic.
        """
        return (f"{self.name}_condition", self.condition_fn)

    def generate_forward_code(self) -> str:
        """Generate conditional code for the DSPy Module"""
        return f"""
        # Conditional: {self.name}
        if self._{self.name.replace(' ', '_').lower()}_condition(state, context):
            next_node = '{self.true_branch}'
        else:
            next_node = '{self.false_branch}'
        state['next_node'] = next_node
"""


class RouterRunnable(Runnable[StateT, ContextT, OutputT]):
    """
    LLM-based routing.
    Compiles to: dspy.ChainOfThought with routing signature
    """

    router_signature: type[dspy.Signature]
    possible_routes: list[str]
    _router: Any = None

    def model_post_init(self, __context):
        """Initialize router"""
        self._router = dspy.ChainOfThought(self.router_signature)

    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Use LLM to route"""
        inputs = {k: state[k] for k in self.expects.keys() if k in state}
        result = self._router(**inputs)

        next_node = result.route if hasattr(result, 'route') else result.next_step

        return {
            "next_node": next_node,
            "reasoning": result.reasoning if hasattr(result, 'reasoning') else "",
            **state
        }

    def to_dspy_component(self) -> tuple[str, Any]:
        """Returns the router predictor"""
        component_name = f"{self.name.replace(' ', '_').lower()}_router"
        return (component_name, self._router)


class ToolRunnable(Runnable[StateT, ContextT, OutputT]):
    """
    Tool execution.
    Compiles to: dspy.Tool wrappers
    """

    tools: list[Callable]
    tool_signature: type[dspy.Signature] | None = None
    _tool_selector: Any = None
    _tool_map: dict = None

    def model_post_init(self, __context):
        """Setup tools"""
        self._tool_map = {tool.__name__: tool for tool in self.tools}

        if self.tool_signature:
            self._tool_selector = dspy.ChainOfThought(self.tool_signature)

    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Execute tool"""
        if self._tool_selector:
            inputs = {k: state[k] for k in self.expects.keys() if k in state}
            decision = self._tool_selector(**inputs)
            tool_name = decision.tool_name
            tool_args = decision.tool_args if hasattr(decision, 'tool_args') else {}
        else:
            tool_name = list(self._tool_map.keys())[0]
            tool_args = state

        result = self._tool_map[tool_name](**tool_args)

        return {
            "tool_result": result,
            "tool_used": tool_name,
            **state
        }

    def to_dspy_component(self) -> tuple[str, Any]:
        """Returns tools as DSPy components"""
        component_name = f"{self.name.replace(' ', '_').lower()}_tools"

        # Wrap tools as dspy.Tool
        dspy_tools = []
        for tool in self.tools:
            dspy_tools.append(dspy.Tool(tool, name=tool.__name__))

        return (component_name, dspy_tools)


# ============= HELPER RUNNABLES =============

class RunnableSequence(Runnable[StateT, ContextT, OutputT]):
    """
    Chain of runnables.
    Compiles to: sequential calls in DSPy Module forward()
    """

    runnables: list[Runnable]

    def forward(self, state: StateT, context: ContextT) -> OutputT:
        """Execute sequence"""
        current_state = state
        for runnable in self.runnables:
            current_state = runnable(current_state, context)
        return current_state

    def to_dspy_component(self) -> tuple[str, Any]:
        """Return all sub-components"""
        components = {}
        for runnable in self.runnables:
            name, component = runnable.to_dspy_component()
            components[name] = component

        return (f"{self.name}_sequence", components)

    def generate_forward_code(self) -> str:
        """Generate sequential execution code"""
        code = f"        # Sequence: {self.name}\n"
        for runnable in self.runnables:
            code += runnable.generate_forward_code()
        return code


# ============= UPDATED COMPILE =============

class CompiledWorkflow:
    """The workflow compiler - generates DSPy Module from Runnables"""

    def __init__(self, name, start_node, layers, end_node, streaming, iterations_max, model):
        self.name = name
        self.start_node = start_node
        self.layers = layers
        self.end_node = end_node
        self.streaming = streaming
        self.iterations_max = iterations_max
        self.model = model
        self._dspy_module = None

    def compile(self) -> dspy.Module:
        """
        Convert the workflow (Runnables) into a DSPy Module.
        """
        # Collect all DSPy components from Runnables
        components = {}
        forward_code_parts = []

        for layer_num, nodes in self.layers.items():
            for node in nodes:
                if isinstance(node, Runnable):
                    # Extract DSPy component
                    comp_name, component = node.to_dspy_component()
                    components[comp_name] = component

                    # Generate forward code
                    forward_code_parts.append(node.generate_forward_code())

        # Generate the DSPy Module class
        module_class = self._generate_module_class(components, forward_code_parts)

        # Instantiate
        self._dspy_module = module_class()

        print(f"✅ [Compile] Generated DSPy Module: {self.name}Module")
        print(f"   Components: {list(components.keys())}")

        return self._dspy_module

    def _generate_module_class(self, components: dict, forward_code_parts: list) -> type[dspy.Module]:
        """Dynamically generate the DSPy Module class"""

        class_name = f"{self.name.replace(' ', '')}Module"

        # Build __init__
        init_code = "    def __init__(self):\n"
        init_code += "        super().__init__()\n"
        for comp_name, component in components.items():
            init_code += f"        self.{comp_name} = components['{comp_name}']\n"

        # Build forward
        forward_code = "    def forward(self, **kwargs):\n"
        forward_code += "        state = kwargs\n"
        forward_code += "        context = kwargs.get('context')\n"
        for code_part in forward_code_parts:
            forward_code += code_part
        forward_code += "        return dspy.Prediction(**state)\n"

        # Combine
        module_code = f"class {class_name}(dspy.Module):\n"
        module_code += init_code
        module_code += forward_code

        # Execute
        namespace = {'dspy': dspy, 'components': components}
        exec(module_code, namespace)

        return namespace[class_name]

    def save(self, path: str):
        """Cloudpickle the compiled DSPy Module"""
        import cloudpickle
        with open(path, 'wb') as f:
            cloudpickle.dump(self._dspy_module, f)

    def optimize(self, trainset, metric, optimizer="mipro"):
        """Optimize the entire workflow as a DSPy Module"""
        from dspy.teleprompt import MIPRO
        teleprompter = MIPRO(metric=metric)
        self._dspy_module = teleprompter.compile(self._dspy_module, trainset=trainset)
        return self


# ============= USAGE =============

# Define a signature runnable
search_sig = SignatureRunnable(
    name="search",
    signature=SearchSignature,
    expects={"query": "string"},
    returns={"context": "array"},
    use_cot=False
)

# This runnable will compile to:
# self.search_predictor = dspy.Predict(SearchSignature)

# Build workflow
workflow = WorkflowBuilder(name="MyWorkflow")
workflow.layer(1, search_sig)
compiled = workflow.compile()

# Now you have a DSPy Module that you can:
compiled.optimize(trainset, metric)  # Optimize the whole workflow
compiled.save("workflow.pkl")         # Serialize it
compiled._dspy_module.inspect_history()  # Debug it
