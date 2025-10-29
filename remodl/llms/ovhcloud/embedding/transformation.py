"""
This is OpenAI compatible - no transformation is applied

"""
from typing import List, Optional, Union

import httpx

from remodl.remodl_core_utils.remodl_logging import Logging as LiteLLMLoggingObj
from remodl.llms.base_llm.chat.transformation import BaseLLMException
from remodl.llms.base_llm.embedding.transformation import BaseEmbeddingConfig
from remodl.secret_managers.main import get_secret_str
from remodl.types.llms.openai import AllEmbeddingInputValues, AllMessageValues
from remodl.types.utils import EmbeddingResponse, Usage

from ..utils import OVHCloudException


class OVHCloudEmbeddingConfig(BaseEmbeddingConfig):
    def __init__(self) -> None:
        pass

    def get_complete_url(
        self,
        api_base: Optional[str],
        api_key: Optional[str],
        model: str,
        optional_params: dict,
        remodl_params: dict,
        stream: Optional[bool] = None,
    ) -> str:
        api_base = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1" if api_base is None else api_base.rstrip("/")
        complete_url = f"{api_base}/embeddings"
        return complete_url

    def validate_environment(
        self,
        headers: dict,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        remodl_params: dict,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> dict:
        if api_key is None:
            api_key = get_secret_str("OVHCLOUD_API_KEY")

        default_headers = {
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        if "Authorization" in headers:
            default_headers["Authorization"] = headers["Authorization"]

        return {**default_headers, **headers}

    def get_supported_openai_params(self, model: str):
        return []

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        model: str,
        drop_params: bool,
    ):
        supported_openai_params = self.get_supported_openai_params(model)
        for param, value in non_default_params.items():
            if param in supported_openai_params:
                optional_params[param] = value
        return optional_params

    def transform_embedding_request(
        self,
        model: str,
        input: AllEmbeddingInputValues,
        optional_params: dict,
        headers: dict,
    ) -> dict:
        return {"input": input, "model": model, **optional_params}

    def transform_embedding_response(
        self,
        model: str,
        raw_response: httpx.Response,
        model_response: EmbeddingResponse,
        logging_obj: LiteLLMLoggingObj,
        api_key: Optional[str],
        request_data: dict,
        optional_params: dict,
        remodl_params: dict,
    ) -> EmbeddingResponse:
        try:
            raw_response_json = raw_response.json()
        except Exception:
            raise OVHCloudException(
                message=raw_response.text,
                status_code=raw_response.status_code,
                headers=raw_response.headers,
            )

        model_response.model = raw_response_json.get("model")
        model_response.data = raw_response_json.get("data")
        model_response.object = raw_response_json.get("object")

        usage = Usage(
            prompt_tokens=raw_response_json.get("usage", {}).get("prompt_tokens", 0),
            total_tokens=raw_response_json.get("usage", {}).get("total_tokens", 0),
        )

        model_response.usage = usage
        return model_response

    def get_error_class(
        self, error_message: str, status_code: int, headers: Union[dict, httpx.Headers]
    ) -> BaseLLMException:
        return OVHCloudException(
            message=error_message, status_code=status_code, headers=headers
        )
