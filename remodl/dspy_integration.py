"""
DSPy Integration with RemodlAI SDK

This module provides a shim layer that makes DSPy use remodl instead of litellm.
When DSPy tries to import litellm, it will get remodl instead.

Usage:
    from remodl import dspy
    
    # DSPy now uses remodl under the hood!
    cot = dspy.ChainOfThought("question -> answer")
    result = cot(question="What is AI?")  # Uses remodl.completion()
"""

import sys

# SHIM: Make DSPy think 'litellm' is actually 'remodl'
# CRITICAL: This must happen BEFORE any DSPy imports
# When DSPy does "import litellm", Python will return remodl
if 'litellm' not in sys.modules:
    # Import remodl at module level to avoid circular imports
    from . import completion, embedding, search
    # Create a module-like object with remodl's functions
    import types
    litellm_shim = types.ModuleType('litellm')
    litellm_shim.completion = completion
    litellm_shim.embedding = embedding  
    litellm_shim.search = search
    litellm_shim.__version__ = __import__('remodl').__version__
    
    # Install the shim
    sys.modules['litellm'] = litellm_shim

# Now import DSPy - it will use remodl for all LLM calls
import dspy

# Re-export DSPy
__all__ = ['dspy']

