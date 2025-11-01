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
teacher_lm = dspy.LM("openrouter/anthropic/claude-sonnet-4.5", api_key="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")

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

# Define LLM-as-a-judge metric
class AssessDSPyCode(dspy.Signature):
    """Assess whether generated DSPy signature code is valid and follows best practices."""
    
    generated_code: str = dspy.InputField(desc="The generated DSPy signature code to assess")
    template: str = dspy.InputField(desc="The correct DSPy signature format template")
    assessment: str = dspy.OutputField(desc="Detailed assessment of code quality and correctness")
    is_valid: bool = dspy.OutputField(desc="Whether the code is valid DSPy syntax")
    score: float = dspy.OutputField(desc="Quality score from 0.0 to 1.0")

# Create judge program
judge = dspy.ChainOfThought(AssessDSPyCode)

# Define evaluation metric
def validate_dspy_signature(gold, pred, trace=None):
    """
    LLM-as-a-judge metric for DSPy signature validation.
    
    Uses an LLM to assess code quality, validity, and adherence to DSPy patterns.
    Falls back to syntax checking for safety.
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
    
    # Quick syntax check first (fail fast)
    try:
        compile(pred_code, '<string>', 'exec')
    except SyntaxError:
        return 0.0  # Invalid Python
    
    # Basic validation (must have dspy.Signature)
    if '(dspy.Signature)' not in pred_code:
        return 0.0  # Not a DSPy signature
    
    # Use LLM judge for detailed assessment
    try:
        assessment = judge(
            generated_code=pred_code,
            template=signature_template
        )
        
        # During bootstrapping (trace is not None), return bool
        if trace is not None:
            return assessment.is_valid and assessment.score >= 0.7
        
        # During evaluation, return float score
        return float(assessment.score)
        
    except Exception as e:
        # Fallback to basic scoring if LLM judge fails
        print(f"Judge failed: {e}, using fallback scoring")
        
        score = 0.5  # Base score for valid syntax
        
        # Bonus points for good patterns
        if 'dspy.InputField(' in pred_code:
            score += 0.15
        if 'dspy.OutputField(' in pred_code:
            score += 0.15
        if '"""' in pred_code:
            score += 0.1
        if 'desc=' in pred_code:
            score += 0.1
        
        return min(score, 1.0)

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

