from typing import List, Optional

import remodl
from remodl.llms.base_llm.base_utils import BaseLLMModelInfo
from remodl.secret_managers.main import get_secret_str
from remodl.types.llms.openai import AllMessageValues


class AzureFoundryModelInfo(BaseLLMModelInfo):
    @staticmethod
    def get_api_base(api_base: Optional[str] = None) -> Optional[str]:
        return (
                api_base
                or remodl.api_base
                or get_secret_str("AZURE_AI_API_BASE")
        )
    
    @staticmethod
    def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
        return (
                api_key
                or remodl.api_key
                or remodl.openai_key
                or get_secret_str("AZURE_AI_API_KEY")
            )
    
    @property
    def api_version(self, api_version: Optional[str] = None) -> Optional[str]:
        api_version = (
            api_version
            or remodl.api_version
            or get_secret_str("AZURE_API_VERSION")
        )
        return api_version
    
    #########################################################
    # Not implemented methods
    #########################################################
        

    @staticmethod
    def get_base_model(model: str) -> Optional[str]:
        raise NotImplementedError("Azure Foundry does not support base model")

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
        """Azure Foundry sends api key in query params"""
        raise NotImplementedError("Azure Foundry does not support environment validation")
