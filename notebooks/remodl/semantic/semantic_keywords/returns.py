from pydantic import BaseModel, Field
from typing import Optional, List, Any
from .returns_field import ReturnsField


class Returns(BaseModel):
    fields: List[ReturnsField] = Field(description="A list of fields")
    demos: Optional[List[dict[str, Any]]] = Field(description="A list of examples of the fields")
