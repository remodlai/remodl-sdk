from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal


class ReturnsField(BaseModel):
    name: str = Field(description="The name of the field")
    type: Literal[
        str, int, float, bool, List[str], List[int], List[float], List[bool]
    ] = Field(description="The type of the field")
    description: str = Field(description="A description of the field")
    demos: Optional[List[dict[str, Any]]] = Field(
        description="A list of examples of the field"
    )


class ReturnAsField(BaseModel):
    return_as: str = Field(
        description="The name of the field to return as, e.g 'json', 'dict', 'list', 'str', 'int', 'float', 'bool'"
    )
