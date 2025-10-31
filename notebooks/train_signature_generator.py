"""
Train SignatureGenerator to convert natural language → DSPy signatures

Uses semantic keyword parsing to generate proper DSPy signature code
from natural language task descriptions.
"""

import dspy
import pandas as pd
from dspy.evaluate import Evaluate
from dspy.teleprompt import BootstrapFewShot, MIPROv2
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Load training data
df = pd.read_csv("dspy_signature_training_dataset.csv")
print(f"Loaded {len(df)} training examples")

# Configure DSPy
dspy.configure(
    lm=dspy.LM("openrouter/mistralai/codestral-2508", api_key="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"),  # Student model
    adapter=dspy.JSONAdapter()
)

# Teacher model for optimization
teacher_lm = dspy.LM("openrouter/qwen/qwen3-235b-a22b-thinking-2507", api_key="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")

# Define the signature template and keywords (from dspy_signature_template.py)
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

# Define the SignatureGenerator signature
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
    signature_code: str = dspy.OutputField(desc="Valid Python code following DSPy format exactly")

# Create the program
class SignatureGeneratorProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(SignatureGenerator)
    
    def forward(self, task_description):
        return self.generate(task_description=task_description)

# Prepare training data
trainset = []
for _, row in df.iterrows():
    example = dspy.Example(
        task_description=row['natural_language'],
        signature_code=row['code']
    ).with_inputs('task_description')
    trainset.append(example)

# Split train/dev
split_point = int(len(trainset) * 0.8)
train = trainset[:split_point]
dev = trainset[split_point:]

print(f"\nTrain: {len(train)} examples")
print(f"Dev: {len(dev)} examples")

# Define evaluation metric
def validate_dspy_signature(gold, pred, trace=None):
    """
    Validate that generated code is a proper DSPy Signature.
    
    Checks:
    1. Inherits from dspy.Signature (not just 'Signature')
    2. Has docstring
    3. Uses dspy.InputField() and dspy.OutputField()
    4. Uses 'desc' parameter (not 'description')
    5. No comments like "# Input fields"
    6. Proper type annotations (field: type = ...)
    7. Code is syntactically valid Python
    """
    if not pred or not hasattr(pred, 'signature_code'):
        return 0.0
    
    pred_code = pred.signature_code
    
    # Remove code fences if present
    if '```python' in pred_code:
        try:
            pred_code = pred_code.split('```python')[1].split('```')[0].strip()
        except IndexError:
            return 0.0
    
    score = 0.0
    errors = []
    
    # CRITICAL: Must inherit from dspy.Signature (not just Signature)
    if 'class' in pred_code and '(dspy.Signature)' in pred_code:
        score += 0.2
    else:
        errors.append("Missing 'class X(dspy.Signature)'")
        return 0.0  # Fail fast
    
    # CRITICAL: Must have docstring
    if '"""' in pred_code:
        score += 0.1
    else:
        errors.append("Missing docstring")
    
    # CRITICAL: Must have at least one InputField
    if 'dspy.InputField(' in pred_code:
        score += 0.15
    else:
        errors.append("No dspy.InputField() found")
        return score * 0.5  # Partial credit
    
    # CRITICAL: Must have at least one OutputField
    if 'dspy.OutputField(' in pred_code:
        score += 0.15
    else:
        errors.append("No dspy.OutputField() found")
        return score * 0.5  # Partial credit
    
    # RULE: Must use 'desc' not 'description'
    if 'description=' in pred_code and 'dspy.InputField' in pred_code or 'dspy.OutputField' in pred_code:
        errors.append("Uses 'description=' instead of 'desc='")
        score -= 0.1
    
    # RULE: Should not have comments like "# Input fields"
    if '# Input' in pred_code or '# Output' in pred_code:
        errors.append("Contains comments like '# Input fields'")
        score -= 0.05
    
    # VALIDATION: Try to parse as Python
    try:
        compile(pred_code, '<string>', 'exec')
        score += 0.2  # Valid Python syntax
    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")
        score -= 0.2
    
    # VALIDATION: Check type annotation format (field: type = ...)
    import re
    # Look for pattern: word: word = dspy.
    if re.search(r'\w+:\s*\w+\s*=\s*dspy\.(Input|Output)Field', pred_code):
        score += 0.1
    else:
        errors.append("Incorrect type annotation format")
    
    # BONUS: Try to actually execute and instantiate
    try:
        exec_globals = {'dspy': dspy}
        exec(pred_code, exec_globals)
        # Find the class that was defined
        sig_class = None
        for name, obj in exec_globals.items():
            if isinstance(obj, type) and issubclass(obj, dspy.Signature) and obj != dspy.Signature:
                sig_class = obj
                break
        
        if sig_class:
            score += 0.1  # Successfully created signature class
            
            # Try to instantiate
            try:
                instance = sig_class()
                score += 0.05  # Can instantiate
            except Exception:
                pass
    except Exception as e:
        errors.append(f"Cannot execute: {e}")
    
    if errors and trace:
        print(f"Validation errors: {errors}")
    
    return max(0.0, min(score, 1.0))  # Clamp between 0 and 1

# Create baseline program
print("\n" + "="*60)
print("Creating baseline program...")
print("="*60)
program = SignatureGeneratorProgram()

# Evaluate baseline
print("\nEvaluating baseline...")
baseline_eval = Evaluate(
    devset=dev,
    metric=validate_dspy_signature,
    num_threads=1,
    display_progress=True,
    display_table=5
)
baseline_score = baseline_eval(program)
print(f"\n📊 Baseline Score: {baseline_score}")

# Optimize with BootstrapFewShot
print("\n" + "="*60)
print("Optimizing with BootstrapFewShot...")
print("="*60)

optimizer = BootstrapFewShot(
    metric=validate_dspy_signature,
    max_bootstrapped_demos=4,
    max_labeled_demos=8,
    max_rounds=1,
    teacher_settings=dict(lm=teacher_lm)
)

optimized_program = optimizer.compile(
    student=program,
    trainset=train
)

# Evaluate optimized program
print("\nEvaluating optimized program...")
eval_optimized = Evaluate(
    devset=dev,
    metric=validate_dspy_signature,
    num_threads=1,
    display_progress=True,
    display_table=5
)
optimized_score = eval_optimized(optimized_program)

# Results
print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Baseline Score:  {baseline_score}")
print(f"Optimized Score: {optimized_score}")

# Save the optimized program
save_path = "./signature_generator_optimized.json"
optimized_program.save(save_path)
print(f"\n✅ Optimized program saved to: {save_path}")

# Test on a new example
print("\n" + "="*60)
print("TESTING ON NEW EXAMPLE")
print("="*60)

test_description = """
I need to analyze customer feedback.

You will receive feedback text.
You will receive the product category.
You may receive previous feedback for context.

You must identify the main sentiment.
You can extract specific issues mentioned.
You should rate urgency.

You will return the sentiment (positive/negative/neutral).
You will return a list of issues found.
You will return an urgency score from 1 to 5.
"""

print("\nInput:")
print(test_description)
print("\nGenerated Signature:")

result = optimized_program(task_description=test_description)
print(result.signature_code)

# Calculate cost
if hasattr(dspy.settings, 'lm') and hasattr(dspy.settings.lm, 'history'):
    total_calls = len(dspy.settings.lm.history)
    print(f"\n💰 Total LLM calls: {total_calls}")

print("\n✅ Training complete!")

