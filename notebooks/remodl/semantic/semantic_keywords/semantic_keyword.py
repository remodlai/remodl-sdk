from pydantic import BaseModel, Field
from typing import Optional, List
from .semantic_keyword_example import SemanticKeywordExample


class SemanticKeyword(BaseModel):
    keyword: str = Field(description="The keyword to identify in the statement")
    alt_keywords: Optional[List[str]] = Field(
        description="Other keywords that are synonymous with the keyword"
    )
    examples: List[SemanticKeywordExample] = Field(
        description="A list of examples of the keyword"
    )
    description: str = Field(description="A description of the keyword")


class SemanticKeywords(BaseModel):
    keywords: List[SemanticKeyword] = Field(description="A list of keywords")
