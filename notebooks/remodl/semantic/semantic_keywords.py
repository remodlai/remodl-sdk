
import dspy
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from typing import Literal

# student_lm=dspy.LM(
#         "openrouter/mistralai/codestral-2508",
#         api_key="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",

#     )



class ExpectsField(BaseModel):
    name: str = Field(description="The name of the field")
    type: Literal[str, int, float, bool, list[str], list[int], list[float], list[bool]] = Field(description="The type of the field")
    required: bool = Field(description="Whether the field is required")
    description: str = Field(description="A description of the field")
    demos: Optional[list[dict[str, Any]]] = Field(description="A list of examples of the field")

class ReturnsField(BaseModel):
    name: str = Field(description="The name of the field")
    type: Literal[str, int, float, bool, list[str], list[int], list[float], list[bool]] = Field(description="The type of the field")
    description: str = Field(description="A description of the field")
    demos: Optional[list[dict[str, Any]]] = Field(description="A list of examples of the field")
class ReturnAsField(BaseModel):
    return_as: str = Field(description="The name of the field to return as, e.g 'json', 'dict', 'list', 'str', 'int', 'float', 'bool'")

class Expects(BaseModel):
    fields: list[ExpectsField] = Field(description="A list of fields")
    demos: Optional[list[dict[str, Any]]] = Field(description="A list of examples of the fields")

class Returns(BaseModel):
    fields: list[ReturnsField] = Field(description="A list of fields")
    demos: Optional[list[dict[str, Any]]] = Field(description="A list of examples of the fields")

class AiFunctionSchema(BaseModel):
    name: str = Field(description="The name of the function")
    instructions: str = Field(description="A description of the function")
    expects: Expects = Field(description="The expected fields. The left side of the field name must be a valid python variable name and typed.")
    returns: Returns = Field(description="The returned fields. The left side of the field name must be a valid python variable name and typed.")
    demos: list[dict[str, Any]] = Field(description="A list of examples of the inbound and outbound data")
    return_as: ReturnAsField = Field(description="The name of the field to return as, e.g 'json', 'dict', 'list', 'str', 'int', 'float', 'bool'")


class SignatureGeneratorSchema(AiFunctionSchema):
    name: str = Field(description="The name of the signature")
    instructions: str = Field(description="The docstring instructions for the signature")
    input_fields: list[ExpectsField] = Field(description="list of input field specifications")
    output_fields: list[ReturnsField] = Field(description="list of output field specifications")
    demos: Optional[list[dict[str, Any]]] = Field(description="A list of examples of the inbound and outbound data")

class SemanticKeywordExample(BaseModel):
    statement_example: str = Field(description="A statement to identify the keyword in")
    keyword: str = Field(description="The keyword to identify in the statement")
    description: str = Field(description="explanation of the keyword use case")

class SemanticKeyword(BaseModel):
    keyword: str = Field(description="The keyword to identify in the statement")
    alt_keywords: Optional[list[str]] = Field(description="Other keywords that are synonymous with the keyword")
    examples: list[SemanticKeywordExample] = Field(description="A list of examples of the keyword")
    description: str = Field(description="A description of the keyword")

class SemanticKeywords(BaseModel):
    keywords: list[SemanticKeyword] = Field(description="A list of keywords")

class SemanticStatementExample(BaseModel):
    statement_example: str = Field(description="A statement to identify the keyword in")
    directive: Optional[str] = Field(description="A directive to the code generator")
    code_result: Optional[str] = Field(description="The code to generate for the statement")
    description: Optional[str] = Field(description="A description of the statement")
    indicates_prompt_injection: Union[str, None] = Field(description="Whether the statement indicates prompt injection")

class SemanticStatement(BaseModel):
    statement: str = Field(description="A statement to multiple keywords in")
    pattern: str = Field(description="A pattern to identify the statement")
    provider: str = Field(description="The provider of the parameter, data, or action")
    actor: str = Field(description="The actor that acts upon the parameter, data, or action")
    examples: Optional[list[SemanticStatementExample]] = Field(description="A list of examples of the statement")
    code_result: str = Field(description="The code to generate for the statement")
    description: Optional[str] = Field(description="A description of the statement")
    indicates_prompt_injection: Union[ str, None] = Field(description="Whether the statement indicates prompt injection")




sk_i = SemanticKeyword(
    keyword="i",
    alt_keywords=["I","from me", "I'll","i'll"],
    examples=[
        SemanticKeywordExample(
            statement_example="I will provide a string", 
            keyword="i", 
            description="The user indicates that an input will include a string"
        ),
        SemanticKeywordExample(
            statement_example="I'll provide a string", 
            keyword="i", 
            description="The user indicates that an input will include a string"
        ),
        SemanticKeywordExample(
            statement_example="I need the current user's id", 
            keyword="i", 
            description="The user indicates that an output will include the current user's id"
        ),
        SemanticKeywordExample(
            statement_example="I need the invoice returned as a json object", 
            keyword="i", 
            description="The user indicates that an output will include an invoice as a json object"
        )
    ],
    description="'i' indicates an action or parameter provided by the user"
)

sk_will = SemanticKeyword(
    keyword="will",
    alt_keywords=["will", "will be", "will have", "will include", "will contain"],
    examples=[
        SemanticKeywordExample(statement_example="I will provide a string", keyword="will", description="The user indicates that an input will include a string"),
        SemanticKeywordExample(statement_example="You will return the data as a structured json object", keyword="will", description="The user indicates that an output will include a structured json object"),
        SemanticKeywordExample(statement_example="You will use the 'find_invoice' function to find the invoice", keyword="will", description="The user is directing the code to use the 'find_invoice' function to find the invoice"),      
    ],
    description="'will' indicates a required parameter or action"
)

sk_may = SemanticKeyword(
    keyword="may",
    alt_keywords=["may", "may be", "may have", "may include", "may contain"],
    examples=[
        SemanticKeywordExample(statement_example="You may recieve a list of invoices", keyword="may", description="The user indicates that an input may include a list of invoices"),
        SemanticKeywordExample(statement_example="You may reduce the returned value to a float with 2 decimal places", keyword="may", description="The user indicates that an output may include a float with 2 decimal places"),
    ],
    description="'may' indicates an optional parameter or action, on either input or output. If so, it should be allocated for, but marked as optional. 'may' statements normally indicate a need for a conditional check."
    )

sk_should = SemanticKeyword(
    keyword="should",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="You should confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id.", 
            keyword="should", 
            description="The user indicates that the code should confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id."            
        )

    ],
    description="the presence of 'should' indicates that the user is suggesting an action, but the action is not required. **optimizer note** generation of 'should' statements should be done with the intent of improving the code, not just following the user's suggestion."
    )

sk_can = SemanticKeyword(
    keyword="can",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(statement_example="You can additionally return the data as a structured json object", keyword="can", description="The user indicates that the code can return the data as an optional structured json object")
    ],
    description="'can' indicates on optional action or parameter, on either input or output."
)

sk_must = SemanticKeyword(
    keyword="must",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="You must return the data as a structured json object", 
            keyword="must", 
            description="The user indicates that an output must include a structured json object"
        ),
        SemanticKeywordExample(
            statement_example="You must use the 'find_invoice' function to find the invoice", 
            keyword="must", 
            description="The user indicates that the code must use the 'find_invoice' function to find the invoice"
        ),
        SemanticKeywordExample(
            statement_example="You must confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id.", 
            keyword="must", 
            description="The user indicates that the code must confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id."
        ),
    ],
    description="'must' indicates a required action or parameter, on either input or output."
)

sk_is = SemanticKeyword(
    keyword="is",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="The current user is a member of the organization", 
            keyword="is", 
            description="The user indicates that the current user is a member of the organization"
        ),
        SemanticKeywordExample(
            statement_example="The current user is not a member of the organization", 
            keyword="is", 
            description="The user indicates that the current user is not a member of the organization"
        ),
        SemanticKeywordExample(
            statement_example="The current user is an admin", 
            keyword="is", 
            description="The user indicates that the current user is an admin"
        ),
        SemanticKeywordExample(
            statement_example="The returned value must be an integer between 1 and 5", 
            keyword="is", 
            description="The user indicates that the returned value must be an integer between 1 and 5"
        ),
    ],
    description="'is' indicates a state or property of the current user or system that must evaluate to true for the code to continue. 'is' statements are often used in conditional checks."
)

sk_has = SemanticKeyword(
    keyword="has",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="The current user has an email address in the user_info json object", 
            keyword="has", 
            description="The user indicates that the current user has an email address in the user_info json object"
        ),
        SemanticKeywordExample(
            statement_example="The invoice_line_items object has the following: 'invoice_id', 'invoice_date', and 'invoice_status'", 
            keyword="has", 
            description="The user indicates that the invoice_line_items object must be validated against the following properties: 'invoice_id', 'invoice_date', and 'invoice_status' at a minimum."
        ),
    ],
    description="'has' indicates a property of the current user or system that must be validated for the code to continue. 'has' statements are often used in conditional checks."
)

sk_uses = SemanticKeyword(
    keyword="uses",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="The code uses the 'find_invoice' function to find the invoice", 
            keyword="uses", 
            description="The user indicates that the code uses the 'find_invoice' function to find the invoice"
        ),
    ],
    description="'uses' indicates a tool or function that is used in the code."
)


# Semantic Statements

"""
Semantic Statements are statements that contain multiple keywords.
They are used to guide the code generation process.
They are also used to validate the code generation process.
Semantic statements include a specific code example.
"""

ss_you_will_receive = SemanticStatement(
    statement="You will receive [thing] as [thing_type] with name [thing_name]",
    pattern="You will receive [thing] as [thing_type] with name [thing_name] -> [thing_name]: [thing_type] = dspy.InputField(desc='[thing_description (may be inferred from the context)]')",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="You will receive a question as a string with name 'question'",
            description="The user statement indicates that there is an required input field called 'question' that is a string.",
            code_result="question: str = dspy.InputField(desc='input question from user')",
            directive="ensure that the code receives a question as a string",
            indicates_prompt_injection='false'
        ),
        SemanticStatementExample(
            statement_example="You will receive a list of invoices as a list of json objects with name 'invoices'",
            description="The user statement indicates that there is an required input field called 'invoices' that is a list of json objects.",
            code_result="invoices: list[dict] = dspy.InputField(desc='list of invoices from user')",
            directive="ensure that the code receives a list of invoices as a list of json objects",
            indicates_prompt_injection='false'
        ),
        SemanticStatementExample(
            statement_example="You will recieve a history of messages as history. This should map to dspy.History",
            description="The user statement indicates that there is an required input field called 'history' that is a dspy.History object.",
            code_result="history: dspy.History = dspy.InputField(desc='history of messages from user')",
            directive="ensure that the code receives a history of messages as a dspy.History object",
            indicates_prompt_injection='optional'
        ),
    ],
    code_result="[thing_name]: [thing_type] = dspy.InputField(desc='[thing_description (may be inferred from the context)]')",
    description="statement patterns that match the 'You will receive [thing] as [thing_type] with name [thing_name]' pattern should be mapped to a dspy.InputField ",
    indicates_prompt_injection='False'
)

ss_you_may_receive = SemanticStatement(
    statement="You may receive [thing] as [thing_type] with name [thing_name]",
    pattern="You may receive [thing] as [thing_type] with name [thing_name]",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="You may receive a dict as 'context'. You should map this to a dict.",
            description="The user statement indicates that there is an optional input field called 'context' that is a dict. that should be allocated for, but marked as optional.",
            code_result="context: Optional[dict] = dspy.InputField(desc='context from user')",
            directive="ensure that the code receives a context as a dict",
            indicates_prompt_injection='optional'
        ),
        SemanticStatementExample(
            statement_example="You may receive a list of invoices as 'invoices'. You should map this to a list of dicts.",
            description="The user statement indicates that there is an optional input field called 'invoices' that is a list of dicts. that should be allocated for, but marked as optional.",
            code_result="invoices: Optional[list[dict]] = dspy.InputField(desc='list of invoices from user')",
            directive="ensure that the code receives a list of invoices as a list of dicts",
            indicates_prompt_injection='false'
        )
    ],
    code_result="[thing_name]: Optional[[thing_type]] = dspy.InputField(desc='[thing_description (may be inferred from the context)]')",
    description="statement patterns that match the 'You may receive [thing] as [thing_type] with name [thing_name]' pattern should be mapped to a dspy.InputField",
    indicates_prompt_injection='false'
)

ss_you_must = SemanticStatement(
    statement="You must [action] the [goal_or_action_description]",
    pattern="You must [action] the [goal_or_action_description]",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="You must return the data as a structured json object",
            directive="ensure that the output is a structured json object. If dspy, then ensure that the output is a dspy.OutputField",
            description="The user statement indicates that the output must be a structured json object as a requirement. If dspy, then the output must be a dspy.OutputField",
            code_result="output: str = dspy.OutputField(desc='return the data as a structured json object')",
            indicates_prompt_injection='false'
        ),
        SemanticStatementExample(
            statement_example="You must identify the user's organization by checking the organization id then looking up the user in the organization by the provided user id.",
            directive="ensure that the code identifies the user's organization by checking the organization id then looking up the user in the organization by the provided user id.",
            description="The user statement indicates that the code must identify the user's organization by checking the organization id then looking up the user in the organization by the provided user id.",
            code_result="output: str = dspy.OutputField(desc='return the data as a structured json object')",
            indicates_prompt_injection='true'
        )
    ],
    description="statement patterns that match the 'You must [return, return ascii, return as, return as json, return as dict, return as list, return as str, return as int, return as float, return as bool, etc.] the [goal_or_action_description]' pattern should be mapped to a dspy.OutputField. 'you must' statements that don't indicate a return type, but instead indicate a directive, should be mapped to prompt injection statements, appended to the prompt string.",
    indicates_prompt_injection='optional',
    code_result='none'
)

ss_you_can = SemanticStatement(
    statement="You can [action] the [goal_or_action_description]",
    pattern="You can [action] the [goal_or_action_description]",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="You can use the 'invoice_finder' tool to find the invoice",
            description="The user statement indicates that the code can use the 'invoice_finder' tool to find the invoice",
            code_result="tools=['invoice_finder']",
            directive="ensure that the code can use the 'invoice_finder' tool to find the invoice",
            indicates_prompt_injection='optional'
        ),
        SemanticStatementExample(
            statement_example="You can extract the invoice id from the url",
            description="The user statement indicates an optional reasoning step that can be performed to extract the invoice id from the url",
            code_result=None,
            directive="ensure that the code can extract the invoice id from the url",
            indicates_prompt_injection='true'
        )
    ],
    description="statement patterns that match the 'You can [action] the [goal_or_action_description]' pattern should be mapped to a prompt injection statement, appended to the prompt string. They describe optional or suggested actions or reasoning steps that can be performed to achieve the goal.",
    indicates_prompt_injection='optional',
    code_result='none'
)

ss_is = SemanticStatement(
    statement="The [goal_or_action_description] is [value]",
    pattern="The [goal_or_action_description] is [value]",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="The current user is a member of the organization",
            description="The user statement indicates that the current user is a member of the organization",
            code_result='none',
            directive="ensure that the code checks if the current user is a member of the organization",
            indicates_prompt_injection='true'
        )
    ],
    description="'is' statement indicate truthy or falsy values on the state object. If an 'is' statement is present, then the signature or function must include and expect a passed input that the the 'state' object. For a signature, this would require a dspy.InputField with the name 'state' (e.g. state: [RemodlState | dict] = dspy.InputField(desc='the state object')). It should also return the updated state object as a dspy.OutputField.state( e.g. output_state: [RemodlState | dict] = dspy.OutputField(desc='the updated state object')). statement patterns that match the 'The [goal_or_action_description] is [value]' pattern should be mapped to a prompt injection statement, appended to the prompt string. They describe the state or property of the current user or system that must evaluate to true for the code to continue.",
    indicates_prompt_injection='true',
    code_result='none'
)

ss_has = SemanticStatement(
    statement="The [goal_or_action_description] has [value]",
    pattern="The [goal_or_action_description] has [value]",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="The current user (user_info) has an email address in the user_info json object",
            description="The user statement indicates that the current user has an email address in the user_info json object",
            code_result=None,
            directive="ensure that the code checks if the current user has an email address in the user_info json object",
            indicates_prompt_injection='true'
        ),
        SemanticStatementExample(
            statement_example="The inbound feedback text is at least 25 characters",
            description="The user statement indicates that the inbound feedback text must be at least 25 characters long",
            code_result="feedback_text: str = dspy.InputField(desc='feedback text that must be at least 25 characters')",
            directive="ensure that the code receives a feedback text that is at least 25 characters long",
            indicates_prompt_injection='false'
        )
    ],  
    description="'has' statement indicate validation of a property of the current user or system. If a 'has' statement is present, then the signature or function must include and expect a passed input that the the 'state' object. For a signature, this would require a dspy.InputField with the name 'state' (e.g. state: [RemodlState | dict] = dspy.InputField(desc='the state object')). It should also return the updated state object as a dspy.OutputField.state( e.g. output_state: [RemodlState | dict] = dspy.OutputField(desc='the updated state object')). statement patterns that match the 'The [goal_or_action_description] has [value]' pattern should be mapped to a dspy.InputField. They describe the state or property of the current user or system that must evaluate to true for the code to continue.",
    indicates_prompt_injection='true',
    code_result='none'
)

ss_you_will_return = SemanticStatement(
    statement="You will return [thing] as [thing_type]",
    pattern="You will return [thing] as [thing_type]",
    provider="user",
    actor="you",
    examples=[
        SemanticStatementExample(
            statement_example="You will return the data as a structured json object",
            description="The user statement indicates that the code will return the data as a structured json object",
            code_result="output: str = dspy.OutputField(desc='return the data as a structured json object')",
            directive="ensure that the code returns the data as a structured json object",
            indicates_prompt_injection='false'
        ),
        SemanticStatementExample(
            statement_example="You return the invoice value as 'invoice_value', and the invoice id as 'invoice_id'",
            description="The user statement indicates that the code will return the invoice value as 'invoice_value', and the invoice id as 'invoice_id'",
            code_result="invoice_value: str = dspy.OutputField(desc='the invoice value') invoice_id: str = dspy.OutputField(desc='the invoice id')",
            directive="ensure that the code returns the invoice value as 'invoice_value', and the invoice id as 'invoice_id'",
            indicates_prompt_injection='false'
        )
    ],
    description="statement patterns that match the 'You will return [thing] as [thing_type]' pattern should be mapped to a dspy.OutputField. They describe the output of the function or signature.",
    indicates_prompt_injection='false',
    code_result="output: [thing_type] = dspy.OutputField(desc='[thing_description (may be inferred from the context)]')"
)

semantic_keywords = [sk_i, sk_will, sk_may, sk_should, sk_can, sk_must, sk_is, sk_has, sk_uses]
semantic_statements = [ss_you_will_receive, ss_you_may_receive, ss_you_must, ss_is, ss_has, ss_you_will_return]

keywords_formatted = "\n".join([
    f"{k.keyword}: {k.model_json_schema()}" 
    for k in semantic_keywords
])

statements_formatted = "\n".join([
    f"{s.statement}: {s.model_json_schema()}"
    for s in semantic_statements
])



class SignaturePromptGenerator(dspy.Signature):
    f"""
    You will receive a natural language task description that leverages Remodl's Semantic DSL semantic keywords and statements.
    You will generate a compliant DSPy signature prompt and AiFunctionSchema.
    ***CRITICAL***


    when generating the ai_function_schema, all left side must be a valid python variable name and typed. The right side must be a valid dspy.InputField or dspy.OutputField:
    Good examples:


    Bad examples:
    - question = dspy.InputField()
    - question = dspy.InputField(desc="The question to refine")
    - refined_question = dspy.OutputField()
    - refined_question = dspy.OutputField(desc="The refined question")


    ### Semantic Keywords
    {keywords_formatted}

    ### Semantic Statements
    {statements_formatted}

    ### AI Function Schema
    {{ai_function_schema}}
    """
    user_task: str = dspy.InputField(desc="Natural language task description using semantic keywords and statements")
    signature_name: str = dspy.InputField(desc="The name of the signature")
    examples: list[dict[str, Any]] = dspy.InputField(desc="A list of examples of the inbound and outbound data")
    prompt: str = dspy.OutputField(desc="The DSPy signature prompt")
    ai_function_schema: str = dspy.OutputField(desc="The DSPy AiFunctionSchema")

class Task(BaseModel):
    name: str = Field(description="The name of the task")

    description: str = Field(description="The description of the task")

demos= [
    {
        "statement":"You will receive the user's first name as 'first_name' and last name as 'last_name'.",
        "code_result":"first_name: str = dspy.InputField(desc='the user\'s first name')\nlast_name: str = dspy.InputField(desc='the user\'s last name')"
    },
    {
        "statement":"You will receive a list of invoices as 'invoices'.",
        "code_result":"invoices: list[dict] = dspy.InputField(desc='a list of invoices')"
    },
    {
        "statement":"You will receive a history of messages as 'history'.",
        "code_result":"history: dspy.History = dspy.InputField(desc='a history of messages')"
    },
    {
        "statement":"You will receive a feedback text as 'feedback_text'.",
        "code_result":"feedback_text: str = dspy.InputField(desc='a feedback text')"
    },
    {
        "statement":"You will return the score as an integer between 1 and 10.",
        "code_result":"score: int = dspy.OutputField(desc='a score between 1 and 10')"
    }
],

task2 = Task(
    name="AnalyzeFeedback",

    description= """I need to analyze customer feedback.

You will receive feedback text.
You will receive the product category.
You may receive previous feedback for context.

You must identify the main sentiment.
You can extract specific issues mentioned.
You should rate urgency.

You will return the sentiment (positive/negative/neutral).
You will return a list of issues found.
You will return an urgency score from 1 to 10.
"""
)

task3 = Task(
    name="RefineQuestion",
    description="""
    The name of the signature is '{name}'.
    You will receive a question as 'question'.
    You may receive context as 'context'.
    You must reflect on the question and create an updated version of the question that is optimized for the intent of the query of the user
    You must return the refined question as 'refined_question'.
    """
)

teacher_lm=dspy.LM( "openrouter/anthropic/claude-sonnet-4.5" , base_url="https://openrouter.ai/api/v1", api_key="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")

dspy.configure(lm=teacher_lm, adapter=dspy.JSONAdapter())
prompt_maker = dspy.ChainOfThought(SignaturePromptGenerator)
generated_prompt = prompt_maker(user_task=task3.description, signature_name=task3.name, examples=demos)
print(generated_prompt.ai_function_schema)


test=False

