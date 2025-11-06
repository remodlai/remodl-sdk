"""
Decorators for state initialization and field updates.
"""

from typing import Callable
from functools import wraps
from remodl.agents.state.reducers import append_reducer, replace_reducer, merge_dict_reducer


def chat_state(cls):
    """
    Decorator that initializes a chat state structure.
    
    Usage:
        @chat_state
        class State:
            pass
        
        state = State.init()
    """
    
    def init(**kwargs):
        """Initialize state with chat defaults"""
        default_state = {
            "messages": [],
            "context": {},
            "memory": {},
            "query": "",
            "session_id": "",
            "metadata": {}
        }
        default_state.update(kwargs)
        return default_state
    
    cls.init = staticmethod(init)
    return cls


def messages(reducer: str = "append"):
    """
    Decorator for functions that update messages.
    Automatically applies reducer to state["messages"]
    
    Usage:
        @messages("append")
        def add_user_message(message, state):
            return {"role": "user", "content": message}
            
    Args:
        reducer: Reducer strategy - "append" or "replace"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(data, state):
            # Get the new message(s)
            new_data = func(data, state)
            
            # Apply reducer
            if reducer == "append":
                state["messages"] = append_reducer(state.get("messages", []), new_data)
            elif reducer == "replace":
                state["messages"] = new_data if isinstance(new_data, list) else [new_data]
            
            return state
        
        return wrapper
    return decorator


def context(reducer: str = "merge"):
    """
    Decorator for functions that update context.
    
    Usage:
        @context("merge")
        def add_user_info(info, state):
            return {"user_id": info["id"]}
            
    Args:
        reducer: Reducer strategy - "merge" or "replace"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(data, state):
            new_data = func(data, state)
            
            if reducer == "merge":
                state["context"] = merge_dict_reducer(state.get("context", {}), new_data)
            elif reducer == "replace":
                state["context"] = new_data
            
            return state
        
        return wrapper
    return decorator


def memory(reducer: str = "merge"):
    """
    Decorator for functions that update memory.
    
    Usage:
        @memory("merge")
        def store_preference(pref, state):
            return {"theme": pref}
            
    Args:
        reducer: Reducer strategy - "merge" or "replace"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(data, state):
            new_data = func(data, state)
            
            if reducer == "merge":
                state["memory"] = merge_dict_reducer(state.get("memory", {}), new_data)
            elif reducer == "replace":
                state["memory"] = new_data
            
            return state
        
        return wrapper
    return decorator
