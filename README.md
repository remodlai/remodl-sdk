<h1 align="center">
    <img src="https://lexiq-nova-media.s3.us-east-1.amazonaws.com/Color+logo+-+no+background.svg" alt="RemodlAI" width="400"/>
</h1>

<p align="center">
    <strong>Cognitive AI Infrastructure SDK</strong>
    <br>
    Unified interface for LLMs, embeddings, search, and agentic workflows
</p>

<h4 align="center">
    <a href="https://remodl.ai" target="_blank">Website</a> |
    <a href="https://docs.remodl.ai" target="_blank">Documentation</a> |
    <a href="https://github.com/remodlai/remodl-sdk" target="_blank">GitHub</a>
</h4>

---

## Overview

The Remodl SDK is an enterprise-grade AI infrastructure library that provides a unified API for:

- **🤖 LLM Access** - GPT-4, Claude, Gemini, and 100+ models via single interface
- **🧠 Advanced Embeddings** - Nova multimodal embeddings with task-specific optimization
- **🔍 Web Search** - Integrated search capabilities for RAG and research workflows
- **🎯 DSPy Framework** - Built-in support for complex agentic pipelines
- **💼 Production Ready** - Enterprise features including retry logic, fallbacks, and cost tracking

## Installation

```bash
pip install remodl-ai
```

## Quick Start

### LLM Completions

```python
import remodl

response = remodl.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
print(response.choices[0].message.content)
```

### Nova Embeddings

Our industry-leading multimodal embedding models support text, images, and code:

```python
import remodl

# Generate embeddings
embeddings = remodl.embedding(
    model="nova-embeddings-v1",
    input="Your text here"
)

# Task-optimized variants
embeddings = remodl.embedding(
    model="nova-embeddings-v1-retrieval",  # Optimized for RAG
    input=["query", "document"]
)
```

**Nova Features:**

- Multimodal: Process text, images, and code
- Multi-vector output for enhanced precision
- Task-specific adapters (retrieval, similarity, code search)
- 8192 token context window
- 2048-dimension embeddings

### Web Search

Integrated search for RAG, research, and content discovery:

```python
import remodl

results = remodl.search(
    query="Latest developments in AI agents",
    search_provider="web-search",
    max_results=10
)

for result in results.results:
    print(f"{result.title}: {result.url}")
    print(f"Summary: {result.snippet}\n")
```

### DSPy for Agentic Workflows

Build sophisticated AI agents with minimal code:

```python
from remodl import dspy

# Simple Chain of Thought
class QA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("question -> answer")
  
    def forward(self, question):
        return self.generate(question=question)

qa = QA()
result = qa(question="What is machine learning?")
print(result.answer)
```

**Advanced RAG Pipeline:**

```python
from remodl import dspy

class RAGPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question -> answer")
  
    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

# Deploy immediately
pipeline = RAGPipeline()
answer = pipeline(question="Explain neural networks")
```

## Configuration

### Environment Variables

```bash
# RemodlAI credentials
export REMODL_API_KEY="your-api-key"
export REMODL_API_BASE="https://api.remodl.ai/v1"

# Optional: Direct provider credentials
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Programmatic Setup

```python
import remodl

# Configure credentials
remodl.api_key = "your-api-key"
remodl.api_base = "https://api.remodl.ai/v1"

# Enable detailed logging
remodl.set_verbose = True
```

## Supported Models

### Embeddings

- **Nova Embeddings V1** - Multimodal with task adapters
  - `nova-embeddings-v1` - Auto-routing base model
  - `nova-embeddings-v1-retrieval` - RAG optimized
  - `nova-embeddings-v1-text-matching` - Similarity search
  - `nova-embeddings-v1-code` - Code understanding

### LLMs

- OpenAI: GPT-4, GPT-4 Turbo, GPT-3.5
- Anthropic: Claude 3.5 Sonnet, Claude 3 Opus
- Google: Gemini Pro, Gemini Ultra
- Open Source: Llama 3, Mistral, Mixtral
- And 100+ more models

## Advanced Features

### Streaming Responses

```python
response = remodl.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

### Function Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
}]

response = remodl.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    tools=tools,
    tool_choice="auto"
)
```

### Async Operations

```python
import asyncio
import remodl

async def generate():
    response = await remodl.acompletion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    return response.choices[0].message.content

result = asyncio.run(generate())
```

### Cost Tracking

Automatic cost calculation across all providers:

```python
from remodl import completion_cost

response = remodl.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

cost = completion_cost(completion_response=response)
print(f"Request cost: ${cost:.6f}")
```

## DSPy Examples

### Basic Prediction

```python
from remodl import dspy

predictor = dspy.Predict("question -> answer")
result = predictor(question="What is the capital of France?")
print(result.answer)
```

### Multi-Step Reasoning

```python
from remodl import dspy

class Solver(dspy.Module):
    def __init__(self):
        super().__init__()
        self.think = dspy.ChainOfThought("problem -> reasoning, solution")
  
    def forward(self, problem):
        return self.think(problem=problem)

solver = Solver()
result = solver(problem="If a train travels 120 miles in 2 hours, what's its speed?")
print(f"Reasoning: {result.reasoning}")
print(f"Solution: {result.solution}")
```

### RAG with Search Integration

```python
from remodl import dspy
import remodl

class SearchRAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("context, question -> answer")
  
    def forward(self, question):
        # Use remodl search directly
        search_results = remodl.search(
            query=question,
            search_provider="web-search",
            max_results=5
        )
      
        context = "\n".join([r.snippet for r in search_results.results])
        return self.generate(context=context, question=question)

rag = SearchRAG()
answer = rag(question="Latest AI breakthroughs in 2024")
print(answer.answer)
```

## Best Practices

### API Key Security

```python
# ✓ Good - use environment variables
import os
import remodl

remodl.api_key = os.getenv("REMODL_API_KEY")

# ✗ Bad - hardcoded keys
# remodl.api_key = "sk-1234..."  # Never do this!
```

### Error Handling

```python
import remodl
from remodl.exceptions import AuthenticationError, RateLimitError

try:
    response = remodl.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
```

### Retry Logic

```python
import remodl

# Built-in retry with exponential backoff
remodl.num_retries = 3

response = remodl.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Support & Resources

- **Documentation**: [https://docs.remodl.ai](https://docs.remodl.ai)
- **API Reference**: [https://docs.remodl.ai/api](https://docs.remodl.ai/api)
- **GitHub**: [https://github.com/remodlai/remodl-sdk](https://github.com/remodlai/remodl-sdk)
- **Support**: support@remodl.ai

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<p align="center">
    Made with ❤️ by <a href="https://remodl.ai">RemodlAI</a>
</p>
