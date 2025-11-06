"""
Complete example of using the Remodl Agents framework.
"""

from remodl.agents import (
    # State management
    chat_state, messages, context, memory,
    
    # DSL
    create_agent, workflow, start, end, agentic_router, mcptool,
    
    # Summarizers
    summarizers
)

# ============= STEP 1: DEFINE STATE =============

@chat_state
class State:
    pass

# State updaters with reducers
@messages("append")
def add_user_message(content, state):
    return {"role": "user", "content": content}

@messages("append")
def add_assistant_message(content, state):
    return {"role": "assistant", "content": content}

@context("merge")
def update_user_info(info, state):
    return {"user_id": info.get("id"), "session": info.get("session")}

@memory("merge")
def store_preferences(prefs, state):
    return prefs


# ============= STEP 2: SETUP TOOLS =============

# Connect to MCP server for tools
ducks_db = mcptool("http://ducksdb/mcp")
duck_tools = ducks_db.tools


# ============= STEP 3: CREATE AGENTS =============

foo_agent = create_agent(
    name="Duck Expert",
    role="You are an expert on ducks and answer duck-related questions",
    tools=duck_tools
).with_state(State, context, messages)

bar_agent = create_agent(
    name="General Assistant",
    role="You answer general questions that are not duck-related"
).with_state(State, context, messages)


# ============= STEP 4: CREATE ROUTER =============

duck_router = agentic_router.create(name="duck_router", has_rules=True)
duck_router.add_rule(
    "When the question is about ducks, route to 'Duck Expert'. "
    "Otherwise, route to 'General Assistant'"
)
compiled_router = duck_router.init()


# ============= STEP 5: BUILD WORKFLOW =============

# Create workflow
duck_workflow = workflow.create(
    name='DuckWorkflow',
    streaming=True,
    iterations_max=3,
    model='remodlai/nova-chat-3b'
)

# Define entry and exit
start_node = start.init(expects=["messages", "query", "session_id"])
end_node = end.init(expects=["messages", "answer", "session_id"])

# Build the graph
dw = duck_workflow
dw.starts_at(start_node)
dw.layer(1, compiled_router)  # Router layer
dw.layer(2, [foo_agent, bar_agent])  # Agent layer
dw.ends_at(end_node)


# ============= STEP 6: COMPILE WITH SUMMARIZATION =============

# Option A: Adaptive summarization
compiled = dw.compile(
    summarizer=summarizers.adaptive(
        last_n_msg=5,
        instruct="Analyze the conversation and prioritize immediate context and long-term user details"
    )
)

# Option B: Chronological with aggressive summarization
# compiled = dw.compile(
#     summarizer=summarizers.chrono(
#         last_n_msg=4,
#         max_summary_ratio=0.20
#     )
# )

# Option C: No summarization for development
# compiled = dw.compile(summarizer=summarizers.none())


# ============= STEP 7: INITIALIZE STATE =============

state = State.init(session_id="sess_123")

# Add initial conversation
state = add_user_message("Hello, I want to learn about ducks", state)
state = update_user_info({"id": "user_123", "session": "sess_123"}, state)


# ============= STEP 8: EXECUTE =============

result = compiled(
    messages=state["messages"],
    query="What do ducks eat?",
    session_id="sess_123"
)

print("Answer:", result.answer)
print("Messages:", len(result.messages))


# ============= STEP 9: OPTIMIZE (OPTIONAL) =============

# Create training data
trainset = [
    # ... your training examples
]

def my_metric(example, prediction):
    # ... your evaluation logic
    return 1.0 if prediction.answer else 0.0

# Optimize the workflow
compiled.optimize(
    trainset=trainset,
    metric=my_metric,
    optimizer="mipro"
)


# ============= STEP 10: SAVE & DEPLOY =============

# Save optimized workflow
compiled.save("./workflows/duck_workflow_optimized.pkl")

# Deploy to production
compiled.deploy(
    endpoint="https://api.remodl.ai/deploy",
    api_key="sk-your-api-key"
)


# ============= STEP 11: ACTIVATE A2A (OPTIONAL) =============

# Enable agent-to-agent communication
coordinator = compiled.activateA2A()

# Now agents can:
# - Send messages to each other
# - Find experts by capability
# - Broadcast status updates
# - Request help from specialists

print("✅ Workflow compiled, optimized, and deployed!")
