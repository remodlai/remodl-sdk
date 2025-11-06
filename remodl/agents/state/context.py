"""
Context window management and token estimation.
"""

# Global context window size (tokens)
context_window = 128000


def calc_current_context_window(state: dict) -> int:
    """
    Calculate current token size of state.
    Uses rough estimate: ~4 chars per token
    
    Args:
        state: Current state dictionary
        
    Returns:
        Estimated token count
    """
    total_tokens = 0
    
    # Count message tokens
    for msg in state.get("messages", []):
        content = msg.get("content", "")
        if isinstance(content, str):
            total_tokens += len(content) // 4
        elif isinstance(content, list):
            # Handle structured content (images, etc.)
            for item in content:
                if isinstance(item, dict):
                    total_tokens += len(str(item)) // 4
    
    # Count context tokens
    context_data = state.get("context", {})
    total_tokens += len(str(context_data)) // 4
    
    # Count memory tokens
    memory_data = state.get("memory", {})
    total_tokens += len(str(memory_data)) // 4
    
    return total_tokens


def get_context_ratio(state: dict) -> float:
    """
    Get current context usage ratio (0.0 to 1.0+)
    
    Args:
        state: Current state dictionary
        
    Returns:
        Ratio of current tokens to context window
    """
    current = calc_current_context_window(state)
    return current / context_window


def set_context_window(size: int):
    """
    Set the global context window size.
    
    Args:
        size: Context window size in tokens
    """
    global context_window
    context_window = size
