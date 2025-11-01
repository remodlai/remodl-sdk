from .semantic_statement import SemanticStatement
from .semantic_statement_example import SemanticStatementExample




# Semantic Statements

"""
Semantic Statements are statements that contain multiple keywords.
They are used to guide the code generation process.
They are also used to validate the code generation process.
Semantic statements include a specific code example.
"""
# "You will receive" statement
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

# "You may receive" statement
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

# "You must" statement
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

# "You can" statement
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

# "Is" statement
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

# "Has" statement
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

# "You will return" statement
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

semantic_statements = [ss_you_will_receive, ss_you_may_receive, ss_you_must, ss_you_can, ss_is, ss_has, ss_you_will_return]

__all__ = ["semantic_statements", "ss_you_will_receive", "ss_you_may_receive", "ss_you_must", "ss_you_can", "ss_is", "ss_has", "ss_you_will_return"]    