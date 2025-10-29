from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Optional, Union

import httpx

from remodl.llms.base_llm.chat.transformation import BaseConfig
from remodl.types.llms.openai import AllMessageValues, OpenAITextCompletionUserMessage
from remodl.types.utils import ModelResponse

if TYPE_CHECKING:
    from remodl.remodl_core_utils.remodl_logging import Logging as _LiteLLMLoggingObj

    LiteLLMLoggingObj = _LiteLLMLoggingObj
else:
    LiteLLMLoggingObj = Any


class BaseTextCompletionConfig(BaseConfig, ABC):
    @abstractmethod
    def transform_text_completion_request(
        self,
        model: str,
        messages: Union[List[AllMessageValues], List[OpenAITextCompletionUserMessage]],
        optional_params: dict,
        headers: dict,
    ) -> dict:
        return {}

    def get_complete_url(
        self,
        api_base: Optional[str],
        api_key: Optional[str],
        model: str,
        optional_params: dict,
        remodl_params: dict,
        stream: Optional[bool] = None,
    ) -> str:
        """
        OPTIONAL

        Get the complete url for the request

        Some providers need `model` in `api_base`
        """
        return api_base or ""

    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        remodl_params: dict,
        headers: dict,
    ) -> dict:
        raise NotImplementedError(
            "AudioTranscriptionConfig does not need a request transformation for audio transcription models"
        )

    def transform_response(
        self,
        model: str,
        raw_response: httpx.Response,
        model_response: ModelResponse,
        logging_obj: LiteLLMLoggingObj,
        request_data: dict,
        messages: List[AllMessageValues],
        optional_params: dict,
        remodl_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
        json_mode: Optional[bool] = None,
    ) -> ModelResponse:
        raise NotImplementedError(
            "AudioTranscriptionConfig does not need a response transformation for audio transcription models"
        )
