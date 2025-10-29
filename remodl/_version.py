import importlib_metadata

try:
    version = importlib_metadata.version("remodl-ai")
except Exception:
    version = "unknown"
