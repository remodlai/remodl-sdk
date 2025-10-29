# Changelog

All notable changes to the Remodl SDK will be documented in this file.

## [0.1.0] - 2025-10-29

### Initial Release

The first release of the Remodl SDK brings enterprise-grade AI infrastructure to Python developers.

#### Features

**Core SDK**
- Unified API for 100+ LLM providers
- Support for chat completions, embeddings, and search
- Automatic cost tracking across all providers
- Built-in retry logic and fallback handling
- OpenAI-compatible interface

**Nova Embedding Models**
- `nova-embeddings-v1` - Multimodal embeddings with automatic task routing
- `nova-embeddings-v1-retrieval` - Optimized for RAG and semantic search
- `nova-embeddings-v1-text-matching` - Optimized for similarity and clustering
- `nova-embeddings-v1-code` - Optimized for code understanding and search
- Support for text, images, and code inputs
- Multi-vector output capability
- Runtime instruction tuning
- 8192 token context window
- 2048-dimension output

**Search Integration**
- Built-in web search capabilities
- Multiple search provider support
- Configurable result limits and filtering
- Seamless integration with RAG workflows

**DSPy Framework**
- Integrated DSPy 3.0.3 for agentic workflows
- Zero-configuration setup
- Full access to DSPy modules, optimizers, and signatures
- Automatic cost tracking for DSPy pipelines

**Developer Experience**
- Environment variable support: `REMODL_API_KEY`, `REMODL_API_BASE`
- Async/await support for all operations
- Streaming responses
- Function calling / tool use
- Comprehensive error handling
- Type hints throughout

**Supported Providers**
- OpenAI (GPT-4, GPT-3.5, DALL-E, Whisper, TTS)
- Anthropic (Claude 3.5, Claude 3)
- Google (Gemini Pro, Gemini Ultra)
- AWS Bedrock (Llama, Claude, Titan)
- Azure OpenAI
- Cohere
- And 95+ more providers

#### Requirements

- Python >= 3.8.1, < 4.0
- Core dependencies: httpx, openai, pydantic, tiktoken

---

For detailed usage examples and migration guides, see [README.md](README.md).
