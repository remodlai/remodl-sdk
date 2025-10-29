import asyncio
from typing import TYPE_CHECKING, Any

from remodl.utils import calculate_max_parallel_requests

if TYPE_CHECKING:
    from remodl.router import Router as _Router

    LitellmRouter = _Router
else:
    LitellmRouter = Any


class InitalizeCachedClient:
    @staticmethod
    def set_max_parallel_requests_client(
        remodl_router_instance: LitellmRouter, model: dict
    ):
        remodl_params = model.get("remodl_params", {})
        model_id = model["model_info"]["id"]
        rpm = remodl_params.get("rpm", None)
        tpm = remodl_params.get("tpm", None)
        max_parallel_requests = remodl_params.get("max_parallel_requests", None)
        calculated_max_parallel_requests = calculate_max_parallel_requests(
            rpm=rpm,
            max_parallel_requests=max_parallel_requests,
            tpm=tpm,
            default_max_parallel_requests=remodl_router_instance.default_max_parallel_requests,
        )
        if calculated_max_parallel_requests:
            semaphore = asyncio.Semaphore(calculated_max_parallel_requests)
            cache_key = f"{model_id}_max_parallel_requests_client"
            remodl_router_instance.cache.set_cache(
                key=cache_key,
                value=semaphore,
                local_only=True,
            )
