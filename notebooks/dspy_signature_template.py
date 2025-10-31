

import dspy
student_lm=dspy.LM(
        "openrouter/mistralai/codestral-2508",
        api_key="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",

    )

teacher_lm=dspy.LM(
    "openrouter/qwen/qwen3-235b-a22b-thinking-2507",
    api_key="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",
)

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

details = {
    "instructions": "Refine a question based on the context.",
    "expects": [
        {
            "name": "question", 
            "type": "str", 
            "required": True, 
            "description": "The question to refine"
        },
        {
            "name": "context", 
            "type": "str", 
            "required": False, 
            "description": "The context to use for the refinement"
        }
    ],
    "returns": [
        {
            "name": "refined_question", 
            "type": "str", 
            "required": True, 
            "description": "The refined question"
        }
    ]
}

details_natural = {
    "name": "RefineQuestion",
    "instructions": """
You will expect a question. 
You may be provided context, but it is not required. 
Return the refined question, and nothing else.

Context is a json object with the following fields:
- history: a list of messages between the user and the assistant
- knowledge: an aray of strings, ending in :: and then a unique identified called a ukid, which looks like 'h.dsds.sdsd/sdsd' or 'hdsdsds.*'
- user_info: a json object with the following fields, all of which are optional:
"""
}

class FieldSpec(BaseModel):
    """Specification for a single field in a DSPy signature."""
    name: str = Field(description="The field name")
    type: str = Field(description="The Python type (e.g., 'str', 'int', 'list[str]')")
    description: Optional[str] = Field(default=None, description="Optional description of the field")
    default: Optional[Any] = Field(default=None, description="Optional default value for input fields")


class SignatureSpec(BaseModel):
    """Complete specification for a DSPy signature."""
    name: str = Field(description="The class name for the signature")
    instructions: str = Field(description="The docstring instructions for the signature")
    input_fields: List[FieldSpec] = Field(description="List of input field specifications")
    output_fields: List[FieldSpec] = Field(description="List of output field specifications")


signature_template = """
CORRECT DSPy SIGNATURE FORMAT:

class ClassName(dspy.Signature):
    \\\"\\\"\\\"Brief task description.\\\"\\\"\\\"

    field_name: type = dspy.InputField()
    field_name: type = dspy.InputField(desc="optional description")
    field_name: type = dspy.OutputField()
    field_name: type = dspy.OutputField(desc="optional description")

CRITICAL RULES:
1. Must inherit from 'dspy.Signature' (never just 'Signature')
2. Docstring is brief and describes the task
3. Use 'desc' parameter, NOT 'description'
4. NO comments like "# Input fields" or "# Output fields"
5. Type annotation BEFORE the = sign
6. Format: field_name: type = dspy.InputField(desc="...")

CORRECT EXAMPLES:

Example 1 - Simple:
class EmotionClassifier(dspy.Signature):
    \\\"\\\"\\\"Classify the emotion expressed in a sentence.\\\"\\\"\\\"

    sentence: str = dspy.InputField()
    emotion: str = dspy.OutputField(desc="One of: sadness, joy, love, anger, fear, surprise")

Example 2 - With descriptions:
class CheckCitationFaithfulness(dspy.Signature):
    \\\"\\\"\\\"Verify that the text is based on the provided context.\\\"\\\"\\\"

    context: str = dspy.InputField(desc="facts here are assumed to be true")
    text: str = dspy.InputField()
    faithfulness: bool = dspy.OutputField()

Example 3 - Multiple inputs/outputs:
class AnswerQuestion(dspy.Signature):
    \\\"\\\"\\\"Answer questions with short factoid answers.\\\"\\\"\\\"

    context: list[str] = dspy.InputField(desc="may contain relevant facts")
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="often between 1 and 5 words")

WRONG FORMAT (DO NOT GENERATE):
class Bad(dspy.Signature):
    # Input fields  ← NO COMMENTS
    field: str = dspy.InputField(description="...")  ← USE 'desc' NOT 'description'
"""


keyword_semantics = """
SEMANTIC KEYWORDS IN USER DESCRIPTIONS:
- Will: required parameter → InputField() with no default
- Should: suggested parameter → InputField() with default
- May: optional parameter → InputField() with default=None
- Will return: required output → OutputField()
- Must/Can/Is/Has/Uses: goes in docstring instructions
"""


class SignatureGenerator(dspy.Signature):
    """Generate valid DSPy signature code from natural language task descriptions.

    Parse semantic keywords to determine inputs and outputs. Follow the exact
    DSPy signature format from the template. Output must be valid Python code.

    TEMPLATE TO FOLLOW:
    {template}

    SEMANTIC KEYWORDS:
    {keywords}
    """.format(template=signature_template, keywords=keyword_semantics)

    task_description: str = dspy.InputField(desc="Natural language task description using semantic keywords")
    signature_name: str = dspy.InputField(desc="Class name for the signature (e.g., 'RefineQuestion')")
    signature_code: str = dspy.OutputField(desc="Valid Python code wrapped in ```python blocks, following DSPy format exactly")


# Initialize the generator
generate_signature = dspy.ChainOfThought(SignatureGenerator)


# Example: User writes this (no DSPy knowledge)
user_task = """
I need to refine user questions to be clearer.

You will receive a question string.
You may receive context containing history and knowledge snippets.

You must preserve the original intent.
You can improve clarity and specificity.

You will return the refined question as a string.
"""

# Expected output format:
expected_output = """
```python
class RefineQuestion(dspy.Signature):
    \\\"\\\"\\\"Refine user questions to be clearer while preserving intent.\\\"\\\"\\\"

    question: str = dspy.InputField()
    context: dict = dspy.InputField(desc="optional history and knowledge snippets")
    refined_question: str = dspy.OutputField()
```
"""
# Initialize the signature generator
generate_signature = dspy.ChainOfThought(SignatureGenerator)


# Example: Using semantic keywords
user_task_description = """
I need to refine user questions.

You will receive a question string.
You may receive context with these properties:
- history: previous conversation messages
- knowledge: relevant information (ends with :: and a UKID)
- user_info: optional user data

You must preserve the original intent.
You can improve clarity and specificity.
You should make questions more suitable for search.

You will return the refined question as a string.
"""

create_signature = generate_signature(task_description=user_task_description, signature_name="RefineQuestion")
print(create_signature.signature_code)
