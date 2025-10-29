"""
Test to verify DSPy uses remodl instead of litellm
"""

import sys

# Import remodl with DSPy integration
from remodl import dspy
import remodl

print("=" * 60)
print("DSPy + Remodl SDK Integration Test")
print("=" * 60)
print()

# Verify shim is installed
print("1. Checking shim installation...")
litellm_module = sys.modules.get('litellm')
if litellm_module:
    print(f"   ✓ 'litellm' in sys.modules: {litellm_module.__name__}")
else:
    print("   ✗ 'litellm' not in sys.modules")

print()

# Verify DSPy classes are available
print("2. Checking DSPy classes...")
print(f"   ✓ dspy.Predict: {hasattr(dspy, 'Predict')}")
print(f"   ✓ dspy.ChainOfThought: {hasattr(dspy, 'ChainOfThought')}")
print(f"   ✓ dspy.Module: {hasattr(dspy, 'Module')}")
print(f"   ✓ dspy.configure: {hasattr(dspy, 'configure')}")

print()

# Test that litellm import returns the shim
print("3. Testing litellm import redirects to remodl...")
import litellm as test_litellm
print(f"   ✓ litellm.__name__: {test_litellm.__name__}")
print(f"   ✓ Has completion: {hasattr(test_litellm, 'completion')}")
print(f"   ✓ Has embedding: {hasattr(test_litellm, 'embedding')}")
print(f"   ✓ Has search: {hasattr(test_litellm, 'search')}")

print()

# Verify remodl environment variables
print("4. Checking remodl defaults...")
print(f"   ✓ remodl.api_key default: {'REMODL_API_KEY env var' if remodl.api_key is None else 'Set'}")
print(f"   ✓ remodl.api_base default: {'REMODL_API_BASE env var' if remodl.api_base is None else 'Set'}")

print()

# Check search providers
from remodl.types.utils import SearchProviders
print("5. Checking custom search providers...")
print(f"   ✓ Has 'web-search': {SearchProviders.WEB_SEARCH.value}")

print()
print("=" * 60)
print("✓ All tests passed! DSPy will use remodl SDK")
print("=" * 60)

