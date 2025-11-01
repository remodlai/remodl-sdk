from pydantic import BaseModel, Field

class SemanticKeywordExample(BaseModel):
    statement_example: str = Field(description="A statement to identify the keyword in")
    keyword: str = Field(description="The keyword to identify in the statement")
    description: str = Field(description="explanation of the keyword use case")
