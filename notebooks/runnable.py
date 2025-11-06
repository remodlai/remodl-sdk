import dspy
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional, Type
from dataclasses import dataclass
@dataclass
class Role:
    name: str = ""
    role: str = ""
    allow_instructions: bool = False
    instructions: str | None = None

    @classmethod
    def with_name(self, name: str) -> "Role":
        return self.model_copy(update={"name": name})

    @classmethod
    def with_role(self, role: str) -> "Role":
        return self.model_copy(update={"role": role})

    @classmethod
    def with_allow_instructions(self, allow_instructions: bool) -> "Role":
        return self.model_copy(update={"allow_instructions": allow_instructions})

    @classmethod
    def with_instructions(self, instructions: str) -> "Role":
        return self.model_copy(update={"instructions": instructions})


    @classmethod
    def build(cls, name: str, role: str, allow_instructions: bool, instructions: str | None) -> "Role":
        return cls(
            name=name,
            role=role,
            allow_instructions=allow_instructions,
            instructions=instructions
        )
class Expectation(BaseModel):
    """
    An input that a runnable can expect.
    """
    type: Literal["string", "number", "boolean", "array", "object"] = Field(description="The type of the expectation")
    name: str = Field(description="The name of the expectation")
    default: Optional[Any] = Field(description="The default value of the expectation")
    description: str = Field(description="A description of the expectation")

class Returnable(BaseModel):
    type: Literal["string", "number", "boolean", "array", "object"] = Field(description="The type of the returnable")
    name: str = Field(description="The name of the returnable")
    description: str = Field(description="A description of the returnable")


def expectation_to_field_string(expectation: Expectation, custom_class: Optional[Type] = None) -> str:
    """
    Convert an Expectation to a DSPy field definition string.
    """
    type_map = {
        "string": "str",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": custom_class.__name__ if custom_class else "dict"
    }
    python_type = type_map[expectation.type]
    field_def = f'{expectation.name}: {python_type} = dspy.InputField(desc="{expectation.description}")'
    return field_def

def returnable_to_field_string(returnable: Returnable, custom_class: Optional[Type] = None) -> str:
    """
    Convert a Returnable to a DSPy field definition string.
    """
    type_map = {
        "string": "str",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": custom_class.__name__ if custom_class else "dict"
    }
    python_type = type_map[returnable.type]
    field_def = f'{returnable.name}: {python_type} = dspy.OutputField(desc="{returnable.description}")'
    return field_def


class Runnable(BaseModel):
    expects: dict[str, Expectation] = Field(description="The expected inputs of the runnable")
    name: str = Field(description="The name of the runnable")
    returns: dict[str, Returnable] = Field(description="The expected outputs of the runnable")
    defined_role: bool = Field(description="Whether the runnable has a defined role")
    role: Role = Field(description="If defined_role is true, the role object")
    fly_role: str = Field(description="If defined_role is false, the string role of the runnable")

    def generate_role(self) -> str:
        """Generate the role string for this runnable."""
        has_defined_role = self.defined_role 
        runnable_role = self.role.role if has_defined_role else self.fly_role
        return runnable_role

    def generate_expectations(self) -> list[str]:
        """Generate field strings for all expectations."""
        return [expectation_to_field_string(exp) for exp in self.expects.values()]

    def generate_returns(self) -> list[str]:
        """Generate field strings for all returns."""
        return [returnable_to_field_string(ret) for ret in self.returns.values()]

    def generate_signature(self) -> Type[dspy.Signature]:
        """
        Generate a DSPy Signature class based on expectations and returns.

        Returns:
            A dspy.Signature subclass
        """
        # Get the role for the signature docstring
        role = self.generate_role()

        # Build the signature class dynamically
        signature_name = f"{self.name}Signature"
        class_lines = [
            f"class {signature_name}(dspy.Signature):",
            f'    """{role}"""',
        ]

        # Add input fields
        for exp in self.expects.values():
            field_str = expectation_to_field_string(exp)
            class_lines.append(f"    {field_str}")

        # Add output fields
        for ret in self.returns.values():
            field_str = returnable_to_field_string(ret)
            class_lines.append(f"    {field_str}")

        # Create the signature class
        signature_code = "\n".join(class_lines)
        namespace = {"dspy": dspy}
        exec(signature_code, namespace)
        signature_class = namespace[signature_name]

        return signature_class


# Example usage:
if __name__ == "__main__":
    runnable = Runnable(
        name="SearchAgent",
        expects={
            "query": Expectation(
                type="string",
                name="query",
                default=None,
                description="The search query to execute"
            ),
            "max_results": Expectation(
                type="number",
                name="max_results",
                default=10,
                description="Maximum number of results"
            )
        },
        returns={
            "results": Returnable(
                type="object",
                name="results",
                description="The search results"
            )
        },
        defined_role=False,
        role=Role(name="", role="", allow_instructions=False, instructions=None),
        fly_role="You are a helpful search agent that processes queries and returns relevant results."
    )

    # Generate the signature
    signature = runnable.generate_signature()

    # Print the generated code
    print("Generated Signature Code:")
    print("-" * 50)
    role = runnable.generate_role()
    print(f"class {runnable.name}Signature(dspy.Signature):")
    print(f'    """{role}"""')
    for exp in runnable.expects.values():
        print(f"    {expectation_to_field_string(exp)}")
    for ret in runnable.returns.values():
        print(f"    {returnable_to_field_string(ret)}")
    print("-" * 50)

    # Use it
    predictor = dspy.Predict(signature)
