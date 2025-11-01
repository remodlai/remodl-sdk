from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal


class ExpectsField(BaseModel):
    name: str = Field(description="The name of the field")
    type: Literal[str, int, float, bool, list[str], list[int], list[float], list[bool]] = Field(description="The type of the field")
    required: bool = Field(description="Whether the field is required")
    description: str = Field(description="A description of the field")
    demos: Optional[List[dict[str, Any]]] = Field(description="A list of examples of the field")

