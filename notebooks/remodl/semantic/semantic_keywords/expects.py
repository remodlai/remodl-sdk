from pydantic import BaseModel, Field
from typing import Optional, List, Any
from .expects_field import ExpectsField


class Expects(BaseModel):
    fields: List[ExpectsField] = Field(description="A list of fields")
    demos: Optional[List[dict[str, Any]]] = Field(description="A list of examples of the fields")
