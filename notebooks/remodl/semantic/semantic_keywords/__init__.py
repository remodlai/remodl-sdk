from .semantic_keyword import SemanticKeyword, SemanticKeywords
from .semantic_keyword_example import SemanticKeywordExample
from .expects import Expects
from .returns import Returns

from .semantic_keyword import SemanticKeyword, SemanticKeywords
from .semantic_keyword_example import SemanticKeywordExample
from typing import List


# "I" keyword
sk_i = SemanticKeyword(
    keyword="i",
    alt_keywords=["I", "from me", "I'll", "i'll"],
    examples=[
        SemanticKeywordExample(
            statement_example="I will provide a string",
            keyword="i",
            description="The user indicates that an input will include a string",
        ),
        SemanticKeywordExample(
            statement_example="I'll provide a string",
            keyword="i",
            description="The user indicates that an input will include a string",
        ),
        SemanticKeywordExample(
            statement_example="I need the current user's id",
            keyword="i",
            description="The user indicates that an output will include the current user's id",
        ),
        SemanticKeywordExample(
            statement_example="I need the invoice returned as a json object",
            keyword="i",
            description="The user indicates that an output will include an invoice as a json object",
        ),
    ],
    description="'i' indicates an action or parameter provided by the user",
)

# "Will" keyword
sk_will = SemanticKeyword(
    keyword="will",
    alt_keywords=["will", "will be", "will have", "will include", "will contain"],
    examples=[
        SemanticKeywordExample(
            statement_example="I will provide a string",
            keyword="will",
            description="The user indicates that an input will include a string",
        ),
        SemanticKeywordExample(
            statement_example="You will return the data as a structured json object",
            keyword="will",
            description="The user indicates that an output will include a structured json object",
        ),
        SemanticKeywordExample(
            statement_example="You will use the 'find_invoice' function to find the invoice",
            keyword="will",
            description="The user is directing the code to use the 'find_invoice' function to find the invoice",
        ),
    ],
    description="'will' indicates a required parameter or action",
)

# "May" keyword
sk_may = SemanticKeyword(
    keyword="may",
    alt_keywords=["may", "may be", "may have", "may include", "may contain"],
    examples=[
        SemanticKeywordExample(
            statement_example="You may recieve a list of invoices",
            keyword="may",
            description="The user indicates that an input may include a list of invoices",
        ),
        SemanticKeywordExample(
            statement_example="You may reduce the returned value to a float with 2 decimal places",
            keyword="may",
            description="The user indicates that an output may include a float with 2 decimal places",
        ),
    ],
    description="'may' indicates an optional parameter or action, on either input or output. If so, it should be allocated for, but marked as optional. 'may' statements normally indicate a need for a conditional check.",
)

# "Should" keyword
sk_should = SemanticKeyword(
    keyword="should",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="You should confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id.",
            keyword="should",
            description="The user indicates that the code should confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id.",
        )
    ],
    description="the presence of 'should' indicates that the user is suggesting an action, but the action is not required. **optimizer note** generation of 'should' statements should be done with the intent of improving the code, not just following the user's suggestion.",
)

# "Can" keyword
sk_can = SemanticKeyword(
    keyword="can",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="You can additionally return the data as a structured json object",
            keyword="can",
            description="The user indicates that the code can return the data as an optional structured json object",
        )
    ],
    description="'can' indicates on optional action or parameter, on either input or output.",
)

# "Must" keyword
sk_must = SemanticKeyword(
    keyword="must",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="You must return the data as a structured json object",
            keyword="must",
            description="The user indicates that an output must include a structured json object",
        ),
        SemanticKeywordExample(
            statement_example="You must use the 'find_invoice' function to find the invoice",
            keyword="must",
            description="The user indicates that the code must use the 'find_invoice' function to find the invoice",
        ),
        SemanticKeywordExample(
            statement_example="You must confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id.",
            keyword="must",
            description="The user indicates that the code must confirm the current user is a member of the organization by checking the organization id then looking up the user in the organization by the provided user id.",
        ),
    ],
    description="'must' indicates a required action or parameter, on either input or output.",
)

# "Is" keyword
sk_is = SemanticKeyword(
    keyword="is",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="The current user is a member of the organization",
            keyword="is",
            description="The user indicates that the current user is a member of the organization",
        ),
        SemanticKeywordExample(
            statement_example="The current user is not a member of the organization",
            keyword="is",
            description="The user indicates that the current user is not a member of the organization",
        ),
        SemanticKeywordExample(
            statement_example="The current user is an admin",
            keyword="is",
            description="The user indicates that the current user is an admin",
        ),
        SemanticKeywordExample(
            statement_example="The returned value must be an integer between 1 and 5",
            keyword="is",
            description="The user indicates that the returned value must be an integer between 1 and 5",
        ),
    ],
    description="'is' indicates a state or property of the current user or system that must evaluate to true for the code to continue. 'is' statements are often used in conditional checks.",
)

# "Has" keyword
sk_has = SemanticKeyword(
    keyword="has",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="The current user has an email address in the user_info json object",
            keyword="has",
            description="The user indicates that the current user has an email address in the user_info json object",
        ),
        SemanticKeywordExample(
            statement_example="The invoice_line_items object has the following: 'invoice_id', 'invoice_date', and 'invoice_status'",
            keyword="has",
            description="The user indicates that the invoice_line_items object must be validated against the following properties: 'invoice_id', 'invoice_date', and 'invoice_status' at a minimum.",
        ),
    ],
    description="'has' indicates a property of the current user or system that must be validated for the code to continue. 'has' statements are often used in conditional checks.",
)

# "Uses" keyword
sk_uses = SemanticKeyword(
    keyword="uses",
    alt_keywords=None,
    examples=[
        SemanticKeywordExample(
            statement_example="The code uses the 'find_invoice' function to find the invoice",
            keyword="uses",
            description="The user indicates that the code uses the 'find_invoice' function to find the invoice",
        ),
    ],
    description="'uses' indicates a tool or function that is used in the code.",
)

semantic_keywords = SemanticKeywords(
    keywords=[
        sk_i,
        sk_will,
        sk_may,
        sk_should,
        sk_can,
        sk_must,
        sk_is,
        sk_has,
        sk_uses,
    ]
)

__all__ = [
    "semantic_keywords",
    "sk_i",
    "sk_will",
    "sk_may",
    "sk_should",
    "sk_can",
    "sk_must",
    "sk_is",
    "sk_has",
    "sk_uses",
    "Expects",
    "Returns",
    "SemanticKeyword",
    "SemanticKeywordExample",
    "SemanticKeywords",
]
