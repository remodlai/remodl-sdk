"""
Basic tests for the Remodl Agents framework.
"""

import pytest
from remodl.agents import (
    chat_state, messages, context, memory,
    summarizers
)
from remodl.agents.state.reducers import append_reducer, merge_dict_reducer


def test_state_initialization():
    """Test @chat_state decorator."""
    @chat_state
    class State:
        pass
    
    state = State.init()
    
    assert "messages" in state
    assert "context" in state
    assert "memory" in state
    assert isinstance(state["messages"], list)
    assert isinstance(state["context"], dict)
    assert isinstance(state["memory"], dict)


def test_messages_decorator():
    """Test @messages decorator with append reducer."""
    @chat_state
    class State:
        pass
    
    @messages("append")
    def add_message(content, state):
        return {"role": "user", "content": content}
    
    state = State.init()
    state = add_message("Hello", state)
    
    assert len(state["messages"]) == 1
    assert state["messages"][0]["content"] == "Hello"


def test_context_decorator():
    """Test @context decorator with merge reducer."""
    @chat_state
    class State:
        pass
    
    @context("merge")
    def update_context(data, state):
        return {"key": data}
    
    state = State.init()
    state = update_context("value", state)
    
    assert state["context"]["key"] == "value"


def test_append_reducer():
    """Test append_reducer function."""
    existing = [1, 2, 3]
    new = [4, 5]
    
    result = append_reducer(existing, new)
    assert result == [1, 2, 3, 4, 5]
    
    # Test with single item
    result = append_reducer(existing, 4)
    assert result == [1, 2, 3, 4]


def test_merge_dict_reducer():
    """Test merge_dict_reducer function."""
    existing = {"a": 1, "b": 2}
    new = {"b": 3, "c": 4}
    
    result = merge_dict_reducer(existing, new)
    assert result == {"a": 1, "b": 3, "c": 4}


def test_summarizer_factory():
    """Test summarizer factory functions."""
    # Test default
    config = summarizers.default(last_n_msg=5)
    assert config.name == "default"
    assert config.keep_messages == 5
    assert config.max_ratio == 0.75
    
    # Test chrono
    config = summarizers.chrono(last_n_msg=4, max_summary_ratio=0.20)
    assert config.name == "chrono"
    assert config.keep_messages == 4
    assert config.max_ratio == 0.20
    
    # Test adaptive
    config = summarizers.adaptive(
        last_n_msg=5,
        instruct="Custom instructions"
    )
    assert config.name == "adaptive"
    assert config.custom_instructions == "Custom instructions"
    
    # Test none
    config = summarizers.none()
    assert config is None


def test_workflow_builder():
    """Test WorkflowBuilder API."""
    from remodl.agents.workflow.builder import WorkflowBuilder
    
    builder = WorkflowBuilder(name="TestWorkflow")
    assert builder.name == "TestWorkflow"
    assert isinstance(builder.layers, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
