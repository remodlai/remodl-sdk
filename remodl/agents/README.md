# Remodl Agents Framework

A composable, DSPy-native agent framework with state management, automatic summarization, and agent-to-agent communication.

## Architecture

```
remodl/agents/
├── __init__.py              # Public API exports
├── state/                   # State management with reducers
│   ├── __init__.py
│   ├── decorators.py        # @chat_state, @messages, @context, @memory
│   ├── reducers.py          # append_reducer, merge_dict_reducer, etc.
│   └── context.py           # Context window calculations
├── summarizers/             # Automatic context summarization
│   ├── __init__.py
│   ├── config.py            # SummarizerConfig
│   ├── strategies.py        # SummaryStrategy (DSPy signature)
│   └── factories.py         # default(), chrono(), adaptive(), etc.
├── workflow/                # Workflow compilation
│   ├── __init__.py
│   ├── builder.py           # WorkflowBuilder (fluent API)
│   ├── compiler.py          # CompiledWorkflow (generates DSPy modules)
│   └── nodes.py             # StartNode, EndNode
├── dsl/                     # Clean user-facing API
│   ├── __init__.py
│   ├── agent.py             # create_agent()
│   ├── router.py            # agentic_router
│   ├── tools.py             # mcptool()
│   └── factories.py         # workflow, start, end
└── a2a/                     # Agent-to-agent communication (future)
    └── __init__.py
```

## Quick Start

### 1. Define State

```python
from remodl.agents import chat_state, messages, context, memory

@chat_state
class State:
    pass

# Initialize
state = State.init(session_id="sess_123")

# Define state updaters with reducers
@messages("append")
def add_message(content, state):
    return {"role": "user", "content": content}

@context("merge")
def update_context(info, state):
    return {"user_id": info["id"]}

# Use them
state = add_message("Hello!", state)
state = update_context({"id": "user_123"}, state)
```

### 2. Create Agents

```python
from remodl.agents import create_agent, mcptool

# Load tools from MCP
ducks_db = mcptool("http://ducksdb/mcp")
duck_tools = ducks_db.tools

# Create agents
foo_agent = create_agent(
    name="Duck Expert",
    role="You answer duck related questions",
    tools=duck_tools
).with_state(state, context, messages)

bar_agent = create_agent(
    name="General Agent",
    role="You answer general questions"
).with_state(state, context, messages)
```

### 3. Build Workflow

```python
from remodl.agents import workflow, start, end, agentic_router

# Create router
duck_router = agentic_router.create(name="duck router", has_rules=True)
duck_router.add_rule("when question is duck related tag as 'duck', else 'not_duck'")
duck_router.init()

# Build workflow
dw = workflow.create(
    name='Duck Workflow',
    streaming=True,
    iterations_max=3,
    model='remodlai/nova-chat-3b'
)

start_node = start.init(expects=["messages", "query", "session"])
end_node = end.init(start_node.expects)

dw.starts_at(start_node)
dw.layer(1, duck_router)
dw.layer(2, [foo_agent, bar_agent])
```

### 4. Compile with Summarization

```python
from remodl.agents import summarizers

# Option 1: Use preset
compiled = dw.compile(summarizer="adaptive")

# Option 2: Custom configuration
compiled = dw.compile(
    summarizer=summarizers.adaptive(
        last_n_msg=5,
        instruct="Prioritize user context and project details"
    )
)

# Option 3: Chronological with tight context
compiled = dw.compile(
    summarizer=summarizers.chrono(
        last_n_msg=4,
        max_summary_ratio=0.20
    )
)

# Option 4: No summarization (dev mode)
compiled = dw.compile(summarizer=summarizers.none())
```

### 5. Execute

```python
# Run the workflow
result = compiled(
    messages=[],
    query="What do ducks eat?",
    session="sess_123"
)

print(result.answer)
```

### 6. Optimize & Deploy

```python
# Optimize with DSPy
compiled.optimize(
    trainset=my_data,
    metric=my_metric,
    optimizer="mipro"
)

# Save
compiled.save("./workflows/duck_workflow_v1.pkl")

# Load
loaded = CompiledWorkflow.load("./workflows/duck_workflow_v1.pkl")

# Deploy
compiled.deploy(
    endpoint="https://api.remodl.ai/deploy",
    api_key="sk-..."
)
```

### 7. Agent-to-Agent Communication

```python
# Activate A2A
dw.activateA2A()

# Now agents can communicate:
# - foo_agent.send_to_agent("Bar Agent", {"help": True})
# - bar_agent.find_expert("duck_expert")
# - foo_agent.broadcast({"status": "working"})
```

## Summarization Strategies

### Available Presets

- `default()` - Balanced conversation flow
- `chrono()` - Chronological timeline preservation
- `adaptive()` - LLM-determined importance
- `aggressive()` - Minimal context (cost optimization)
- `conservative()` - Maximum context retention
- `production()` - Production-ready balance
- `none()` - No summarization (development)

### Custom Strategy

```python
from remodl.agents.summarizers import custom

my_summarizer = custom(
    name="medical",
    approach="medical_history",
    prioritize="symptoms_and_diagnosis",
    last_n_msg=3,
    max_summary_ratio=0.80,
    instruct="Maintain medical history and treatment decisions"
)

compiled = dw.compile(summarizer=my_summarizer)
```

## Key Features

1. **State Management with Reducers**
   - `@messages("append")` - Auto-append to message list
   - `@context("merge")` - Auto-merge context dicts
   - `@memory("merge")` - Auto-merge memory

2. **Automatic Summarization**
   - Monitors context window usage
   - Triggers at configurable thresholds
   - Preserves important information
   - Offloads media to storage

3. **DSPy-Native Compilation**
   - Workflows compile to DSPy Modules
   - Optimizable with MIPRO, BootstrapFewShot
   - Serializable with cloudpickle
   - Deployable as single artifacts

4. **Agent-to-Agent Communication**
   - Dynamic agent discovery
   - Message routing
   - Capability-based delegation

## Design Principles

1. **Declarative DSL** - Clean, readable workflow definitions
2. **Compile-Time Optimization** - Configuration at compile, not runtime
3. **Modular Architecture** - Small, focused modules
4. **Type Safety** - Pydantic models throughout
5. **DSPy Integration** - Native support for DSPy signatures and modules

## Development

The framework is organized into logical modules:

- `state/` - State management primitives
- `summarizers/` - Context summarization strategies
- `workflow/` - Workflow building and compilation
- `dsl/` - User-facing API
- `a2a/` - Agent-to-agent communication (future)

Each module is self-contained and can be developed independently.
