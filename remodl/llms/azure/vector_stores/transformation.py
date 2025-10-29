from typing import Optional

from remodl.llms.azure.common_utils import BaseAzureLLM
from remodl.llms.openai.vector_stores.transformation import OpenAIVectorStoreConfig
from remodl.types.router import GenericLiteLLMParams


class AzureOpenAIVectorStoreConfig(OpenAIVectorStoreConfig):
    def get_complete_url(
        self,
        api_base: Optional[str],
        remodl_params: dict,
    ) -> str:
        return BaseAzureLLM._get_base_azure_url(
            api_base=api_base,
            remodl_params=remodl_params,
            route="/openai/vector_stores"
        )


    def validate_environment(
        self, headers: dict,  remodl_params: Optional[GenericLiteLLMParams]
    ) -> dict:
        return BaseAzureLLM._base_validate_azure_environment(
            headers=headers,
            remodl_params=remodl_params
        )