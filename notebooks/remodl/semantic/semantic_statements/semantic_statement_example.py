from pydantic import BaseModel, Field
from typing import Optional

class SemanticStatementExample(BaseModel):
    statement_example: str = Field(description="A statement to identify the keyword in")
    directive: Optional[str] = Field(description="A directive to the code generator")
    code_result: Optional[str] = Field(description="The code to generate for the statement")
    description: Optional[str] = Field(description="A description of the statement")
    indicates_prompt_injection: Optional[str] = Field(description="Whether the statement indicates prompt injection")   