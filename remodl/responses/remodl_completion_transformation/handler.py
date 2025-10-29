"""
Handler for transforming responses api requests to remodl.completion requests
"""

from typing import Any, Coroutine, Dict, Optional, Union

import remodl
from remodl.responses.remodl_completion_transformation.streaming_iterator import (
    LiteLLMCompletionStreamingIterator,
)
from remodl.responses.remodl_completion_transformation.transformation import (
    LiteLLMCompletionResponsesConfig,
)
from remodl.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
from remodl.types.llms.openai import (
    ResponseInputParam,
    ResponsesAPIOptionalRequestParams,
    ResponsesAPIResponse,
)
from remodl.types.utils import ModelResponse


class LiteLLMCompletionTransformationHandler:

    def response_api_handler(
        self,
        model: str,
        input: Union[str, ResponseInputParam],
        responses_api_request: ResponsesAPIOptionalRequestParams,
        custom_llm_provider: Optional[str] = None,
        _is_async: bool = False,
        stream: Optional[bool] = None,
        extra_headers: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Union[
        ResponsesAPIResponse,
        BaseResponsesAPIStreamingIterator,
        Coroutine[
            Any, Any, Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]
        ],
    ]:
        remodl_completion_request: dict = (
            LiteLLMCompletionResponsesConfig.transform_responses_api_request_to_chat_completion_request(
                model=model,
                input=input,
                responses_api_request=responses_api_request,
                custom_llm_provider=custom_llm_provider,
                stream=stream,
                extra_headers=extra_headers,
                **kwargs,
            )
        )

        if _is_async:
            return self.async_response_api_handler(
                remodl_completion_request=remodl_completion_request,
                request_input=input,
                responses_api_request=responses_api_request,
                **kwargs,
            )

        completion_args = {}
        completion_args.update(kwargs)
        completion_args.update(remodl_completion_request)

        remodl_completion_response: Union[
            ModelResponse, remodl.CustomStreamWrapper
        ] = remodl.completion(
            **remodl_completion_request,
            **kwargs,
        )

        if isinstance(remodl_completion_response, ModelResponse):
            responses_api_response: ResponsesAPIResponse = (
                LiteLLMCompletionResponsesConfig.transform_chat_completion_response_to_responses_api_response(
                    chat_completion_response=remodl_completion_response,
                    request_input=input,
                    responses_api_request=responses_api_request,
                )
            )

            return responses_api_response

        elif isinstance(remodl_completion_response, remodl.CustomStreamWrapper):
            return LiteLLMCompletionStreamingIterator(
                model=model,
                remodl_custom_stream_wrapper=remodl_completion_response,
                request_input=input,
                responses_api_request=responses_api_request,
                custom_llm_provider=custom_llm_provider,
                remodl_metadata=kwargs.get("remodl_metadata", {}),
            )

    async def async_response_api_handler(
        self,
        remodl_completion_request: dict,
        request_input: Union[str, ResponseInputParam],
        responses_api_request: ResponsesAPIOptionalRequestParams,
        **kwargs,
    ) -> Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]:

        previous_response_id: Optional[str] = responses_api_request.get(
            "previous_response_id"
        )
        if previous_response_id:
            remodl_completion_request = await LiteLLMCompletionResponsesConfig.async_responses_api_session_handler(
                previous_response_id=previous_response_id,
                remodl_completion_request=remodl_completion_request,
            )

        acompletion_args = {}
        acompletion_args.update(kwargs)
        acompletion_args.update(remodl_completion_request)

        remodl_completion_response: Union[
            ModelResponse, remodl.CustomStreamWrapper
        ] = await remodl.acompletion(
            **acompletion_args,
        )

        if isinstance(remodl_completion_response, ModelResponse):
            responses_api_response: ResponsesAPIResponse = (
                LiteLLMCompletionResponsesConfig.transform_chat_completion_response_to_responses_api_response(
                    chat_completion_response=remodl_completion_response,
                    request_input=request_input,
                    responses_api_request=responses_api_request,
                )
            )

            return responses_api_response

        elif isinstance(remodl_completion_response, remodl.CustomStreamWrapper):
            return LiteLLMCompletionStreamingIterator(
                model=remodl_completion_request.get("model") or "",
                remodl_custom_stream_wrapper=remodl_completion_response,
                request_input=request_input,
                responses_api_request=responses_api_request,
                custom_llm_provider=remodl_completion_request.get(
                    "custom_llm_provider"
                ),
                remodl_metadata=kwargs.get("remodl_metadata", {}),
            )
