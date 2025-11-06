# File Structure

This document explains the organization of the Remodl Agents framework.

## Design Philosophy

The framework follows these principles:

1. **Separation of Concerns** - Each module has a single, well-defined responsibility
2. **Small Modules** - Files are kept small and focused
3. **Clear Dependencies** - Modules depend on abstractions, not implementations
4. **Public API** - User-facing API is separated from internal implementation

## Directory Structure

```
remodl/agents/
│
├── __init__.py                    # Public API - what users import
│
├── state/                         # State Management Module
│   ├── __init__.py               # Exports: chat_state, messages, context, memory
│   ├── decorators.py             # @chat_state, @messages, @context, @memory
│   ├── reducers.py               # append_reducer, merge_dict_reducer
│   └── context.py                # calc_current_context_window, get_context_ratio
│
├── summarizers/                   # Summarization Module
│   ├── __init__.py               # Exports: default, chrono, adaptive, etc.
│   ├── config.py                 # SummarizerConfig (Pydantic model)
│   ├── strategies.py             # SummaryStrategy (DSPy signature), SummaryStruct
│   └── factories.py              # Factory functions: default(), chrono(), etc.
│
├── workflow/                      # Workflow Compilation Module
│   ├── __init__.py               # Exports: WorkflowBuilder, CompiledWorkflow
│   ├── builder.py                # WorkflowBuilder (fluent API)
│   ├── compiler.py               # CompiledWorkflow (generates DSPy modules)
│   └── nodes.py                  # StartNode, EndNode, CompiledStartNode, etc.
│
├── dsl/                          # Domain Specific Language Module
│   ├── __init__.py               # Exports: create_agent, workflow, start, end
│   ├── agent.py                  # create_agent(), AgentBuilder
│   ├── router.py                 # agentic_router, AgenticRouterBuilder
│   ├── tools.py                  # mcptool(), MCPToolWrapper
│   └── factories.py              # workflow, start, end (factory instances)
│
├── a2a/                          # Agent-to-Agent Communication (future)
│   └── __init__.py
│
├── README.md                     # User documentation
├── STRUCTURE.md                  # This file
├── example.py                    # Complete usage example
└── test_agents.py               # Basic tests
```

## Module Responsibilities

### state/ - State Management

**Purpose:** Manage workflow state with reducer pattern

**Key Files:**
- `decorators.py` - Provides `@chat_state`, `@messages`, `@context`, `@memory`
- `reducers.py` - Reducer functions (append, merge, replace)
- `context.py` - Context window calculations

**Dependencies:** None (pure Python)

**Used By:** workflow/compiler.py, dsl/agent.py

### summarizers/ - Context Summarization

**Purpose:** Automatic context window management via summarization

**Key Files:**
- `config.py` - `SummarizerConfig` Pydantic model
- `strategies.py` - DSPy signature and output models
- `factories.py` - User-friendly factory functions

**Dependencies:** dspy, pydantic

**Used By:** workflow/builder.py, workflow/compiler.py

### workflow/ - Workflow Compilation

**Purpose:** Build and compile workflows into DSPy modules

**Key Files:**
- `builder.py` - Fluent API for building workflows
- `compiler.py` - Converts workflow to executable DSPy module
- `nodes.py` - Special nodes (start, end)

**Dependencies:** dspy, state/, summarizers/

**Used By:** dsl/factories.py

### dsl/ - User-Facing API

**Purpose:** Clean, intuitive API for users

**Key Files:**
- `agent.py` - Agent creation (`create_agent()`)
- `router.py` - Router creation (`agentic_router`)
- `tools.py` - Tool integration (`mcptool()`)
- `factories.py` - Workflow factories (`workflow`, `start`, `end`)

**Dependencies:** workflow/

**Used By:** Users directly

### a2a/ - Agent Communication (future)

**Purpose:** Agent-to-agent communication system

**Status:** Stub for future implementation

**Will Include:**
- `coordinator.py` - A2A coordinator
- `registry.py` - Agent registry
- `message_bus.py` - Message routing

## Import Flow

```
User Code
    ↓
remodl.agents.__init__.py (Public API)
    ↓
dsl/ (create_agent, workflow, etc.)
    ↓
workflow/ (builder, compiler)
    ↓
state/ + summarizers/ (core functionality)
```

## Adding New Features

### To add a new summarizer strategy:

1. Add factory function to `summarizers/factories.py`
2. Optionally add custom signature to `summarizers/strategies.py`
3. Export from `summarizers/__init__.py`

### To add a new runnable type:

1. Create file in new `runnables/` module (to be created)
2. Implement `RunnableBase` interface
3. Add `to_dspy_component()` method
4. Export from appropriate module

### To add a new state decorator:

1. Add decorator to `state/decorators.py`
2. Add reducer if needed to `state/reducers.py`
3. Export from `state/__init__.py`

## File Size Guidelines

- **Small** (<200 lines): decorators.py, reducers.py, config.py
- **Medium** (200-400 lines): factories.py, builder.py, strategies.py
- **Large** (400+ lines): compiler.py (acceptable as code generation)

## Testing Strategy

Tests are organized by module:

```
test_agents.py            # Basic tests for all modules
test_state.py            # State management tests (future)
test_summarizers.py      # Summarization tests (future)
test_workflow.py         # Workflow compilation tests (future)
test_dsl.py             # DSL tests (future)
```

## Future Modules

Planned additions:

- `runnables/` - Base classes for different runnable types
- `a2a/` - Agent-to-agent communication
- `storage/` - Media offloading and persistence
- `telemetry/` - Logging and monitoring
- `deployment/` - Deployment utilities

## Design Patterns Used

1. **Factory Pattern** - `factories.py` files create configured objects
2. **Builder Pattern** - `WorkflowBuilder`, `AgentBuilder` for fluent API
3. **Decorator Pattern** - `@chat_state`, `@messages` for state management
4. **Strategy Pattern** - Summarization strategies
5. **Compiler Pattern** - Workflow → DSPy Module transformation
