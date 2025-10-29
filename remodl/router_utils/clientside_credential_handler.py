"""
Utils for handling clientside credentials

Supported clientside credentials:
- api_key
- api_base
- base_url

If given, generate a unique model_id for the deployment.

Ensures cooldowns are applied correctly.
"""

clientside_credential_keys = ["api_key", "api_base", "base_url"]


def is_clientside_credential(request_kwargs: dict) -> bool:
    """
    Check if the credential is a clientside credential.
    """
    return any(key in request_kwargs for key in clientside_credential_keys)


def get_dynamic_remodl_params(remodl_params: dict, request_kwargs: dict) -> dict:
    """
    Generate a unique model_id for the deployment.

    Returns
    - remodl_params: dict

    for generating a unique model_id.
    """
    # update remodl_params with clientside credentials
    for key in clientside_credential_keys:
        if key in request_kwargs:
            remodl_params[key] = request_kwargs[key]
    return remodl_params
