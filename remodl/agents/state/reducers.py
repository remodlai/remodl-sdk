"""
Reducer functions for state field updates.

Reducers define how new values are combined with existing values.
"""

from typing import Any


def append_reducer(existing: list, new: list | Any) -> list:
    """
    Append new items to existing list.
    
    Args:
        existing: Current list value
        new: New value(s) to append
        
    Returns:
        Combined list
    """
    if existing is None:
        existing = []
    if new is None:
        return existing
    if isinstance(new, list):
        return existing + new
    return existing + [new]


def replace_reducer(existing: Any, new: Any) -> Any:
    """
    Replace existing value with new value.
    
    Args:
        existing: Current value (ignored)
        new: New value
        
    Returns:
        New value, or existing if new is None
    """
    return new if new is not None else existing


def merge_dict_reducer(existing: dict, new: dict) -> dict:
    """
    Merge new dictionary into existing dictionary.
    
    Args:
        existing: Current dictionary
        new: New dictionary to merge
        
    Returns:
        Merged dictionary
    """
    if existing is None:
        return new or {}
    if new is None:
        return existing
    return {**existing, **new}
