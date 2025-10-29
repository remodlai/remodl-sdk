from typing import List

from typing_extensions import Dict, Required, TypedDict, override

from remodl.integrations.custom_logger import CustomLogger


class AdapterItem(TypedDict):
    id: str
    adapter: CustomLogger
