from pydantic import BaseModel, Field
from typing import Optional, Union
from .semantic_statement_example import SemanticStatementExample

class SemanticStatement(BaseModel):
    statement: str = Field(description="A statement to multiple keywords in")
    pattern: str = Field(description="A pattern to identify the statement")
    provider: str = Field(description="The provider of the parameter, data, or action")
    actor: str = Field(description="The actor that acts upon the parameter, data, or action")
    examples: Optional[list[SemanticStatementExample]] = Field(description="A list of examples of the statement")
    code_result: str = Field(description="The code to generate for the statement")
    description: Optional[str] = Field(description="A description of the statement")
    indicates_prompt_injection: Union[bool, None] = Field(description="Whether the statement indicates prompt injection")