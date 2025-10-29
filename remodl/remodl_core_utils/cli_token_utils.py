"""
CLI Token Utilities

SDK-level utilities for reading CLI authentication tokens.
This module has no dependencies on proxy code and can be safely imported at the SDK level.
"""

import json
import os
from pathlib import Path
from typing import Optional


def get_cli_token_file_path() -> str:
    """Get the path to the CLI token file"""
    home_dir = Path.home()
    config_dir = home_dir / ".remodl"
    return str(config_dir / "token.json")


def load_cli_token() -> Optional[dict]:
    """Load CLI token data from file"""
    token_file = get_cli_token_file_path()
    if not os.path.exists(token_file):
        return None
    
    try:
        with open(token_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_remodl_gateway_api_key() -> Optional[str]:
    """
    Get the stored CLI API key for use with LiteLLM SDK.
    
    This function reads the token file created by `remodl-proxy login`
    and returns the API key for use in Python scripts.
    
    Returns:
        str: The API key if found, None otherwise
        
    Example:
        >>> import remodl
        >>> api_key = remodl.get_remodl_gateway_api_key()
        >>> if api_key:
        >>>     response = remodl.completion(
        >>>         model="gpt-3.5-turbo",
        >>>         messages=[{"role": "user", "content": "Hello"}],
        >>>         api_key=api_key,
        >>>         base_url="https://your-proxy.com/v1"
        >>>     )
    """
    token_data = load_cli_token()
    if token_data and 'key' in token_data:
        return token_data['key']
    return None
