from typing import Literal, Optional

import remodl
from remodl.exceptions import BadRequestError
from remodl.types.utils import LlmProviders, LlmProvidersSet


def get_supported_openai_params(  # noqa: PLR0915
    model: str,
    custom_llm_provider: Optional[str] = None,
    request_type: Literal[
        "chat_completion", "embeddings", "transcription"
    ] = "chat_completion",
) -> Optional[list]:
    """
    Returns the supported openai params for a given model + provider

    Example:
    ```
    get_supported_openai_params(model="anthropic.claude-3", custom_llm_provider="bedrock")
    ```

    Returns:
    - List if custom_llm_provider is mapped
    - None if unmapped
    """
    if not custom_llm_provider:
        try:
            custom_llm_provider = remodl.get_llm_provider(model=model)[1]
        except BadRequestError:
            return None

    if custom_llm_provider in LlmProvidersSet:
        provider_config = remodl.ProviderConfigManager.get_provider_chat_config(
            model=model, provider=LlmProviders(custom_llm_provider)
        )
    elif custom_llm_provider.split("/")[0] in LlmProvidersSet:
        provider_config = remodl.ProviderConfigManager.get_provider_chat_config(
            model=model, provider=LlmProviders(custom_llm_provider.split("/")[0])
        )
    else:
        provider_config = None

    if provider_config and request_type == "chat_completion":
        return provider_config.get_supported_openai_params(model=model)

    if custom_llm_provider == "bedrock":
        return remodl.AmazonConverseConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "meta_llama":
        provider_config = remodl.ProviderConfigManager.get_provider_chat_config(
            model=model, provider=LlmProviders.LLAMA
        )
        if provider_config:
            return provider_config.get_supported_openai_params(model=model)
    elif custom_llm_provider == "ollama":
        return remodl.OllamaConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "ollama_chat":
        return remodl.OllamaChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "anthropic":
        return remodl.AnthropicConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "anthropic_text":
        return remodl.AnthropicTextConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "fireworks_ai":
        if request_type == "embeddings":
            return remodl.FireworksAIEmbeddingConfig().get_supported_openai_params(
                model=model
            )
        elif request_type == "transcription":
            return remodl.FireworksAIAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
        else:
            return remodl.FireworksAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nvidia_nim":
        if request_type == "chat_completion":
            return remodl.nvidiaNimConfig.get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return remodl.nvidiaNimEmbeddingConfig.get_supported_openai_params()
    elif custom_llm_provider == "cerebras":
        return remodl.CerebrasConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "baseten":
        return remodl.BasetenConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "xai":
        return remodl.XAIChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "ai21_chat" or custom_llm_provider == "ai21":
        return remodl.AI21ChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "volcengine":
        return remodl.VolcEngineConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "groq":
        return remodl.GroqChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "hosted_vllm":
        return remodl.HostedVLLMChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "vllm":
        return remodl.VLLMConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "deepseek":
        return remodl.DeepSeekChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "cohere_chat" or custom_llm_provider == "cohere":
        return remodl.CohereChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "maritalk":
        return remodl.MaritalkConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "openai":
        if request_type == "transcription":
            transcription_provider_config = (
                remodl.ProviderConfigManager.get_provider_audio_transcription_config(
                    model=model, provider=LlmProviders.OPENAI
                )
            )
            if isinstance(
                transcription_provider_config, remodl.OpenAIGPTAudioTranscriptionConfig
            ):
                return transcription_provider_config.get_supported_openai_params(
                    model=model
                )
            else:
                raise ValueError(
                    f"Unsupported provider config: {transcription_provider_config} for model: {model}"
                )
        return remodl.OpenAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "azure":
        if remodl.AzureOpenAIO1Config().is_o_series_model(model=model):
            return remodl.AzureOpenAIO1Config().get_supported_openai_params(
                model=model
            )
        elif remodl.AzureOpenAIGPT5Config.is_model_gpt_5_model(model=model):
            return remodl.AzureOpenAIGPT5Config().get_supported_openai_params(
                model=model
            )
        else:
            return remodl.AzureOpenAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "openrouter":
        return remodl.OpenrouterConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "vercel_ai_gateway":
        return remodl.VercelAIGatewayConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "mistral" or custom_llm_provider == "codestral":
        # mistal and codestral api have the exact same params
        if request_type == "chat_completion":
            return remodl.MistralConfig().get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return remodl.MistralEmbeddingConfig().get_supported_openai_params()
    elif custom_llm_provider == "text-completion-codestral":
        return remodl.CodestralTextCompletionConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "sambanova":
        if request_type == "embeddings":
            remodl.SambaNovaEmbeddingConfig().get_supported_openai_params(model=model)
        else:
            return remodl.SambanovaConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nebius":
        if request_type == "chat_completion":
            return remodl.NebiusConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "wandb":
        if request_type == "chat_completion":
            return remodl.WandbConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "replicate":
        return remodl.ReplicateConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "huggingface":
        return remodl.HuggingFaceChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "jina_ai":
        if request_type == "embeddings":
            return remodl.JinaAIEmbeddingConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "remodlai":
        if request_type == "embeddings":
            return remodl.RemodlAIEmbeddingConfig().get_supported_openai_params(
                model=model
            )
        else:
            return remodl.RemodlAIChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "together_ai":
        return remodl.TogetherAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "databricks":
        if request_type == "chat_completion":
            return remodl.DatabricksConfig().get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return remodl.DatabricksEmbeddingConfig().get_supported_openai_params()
    elif custom_llm_provider == "palm" or custom_llm_provider == "gemini":
        return remodl.GoogleAIStudioGeminiConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "novita":
        return remodl.NovitaConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "vertex_ai" or custom_llm_provider == "vertex_ai_beta":
        if request_type == "chat_completion":
            if model.startswith("mistral"):
                return remodl.MistralConfig().get_supported_openai_params(model=model)
            elif model.startswith("codestral"):
                return (
                    remodl.CodestralTextCompletionConfig().get_supported_openai_params(
                        model=model
                    )
                )
            elif model.startswith("claude"):
                return remodl.VertexAIAnthropicConfig().get_supported_openai_params(
                    model=model
                )
            elif model.startswith("gemini"):
                return remodl.VertexGeminiConfig().get_supported_openai_params(
                    model=model
                )
            else:
                return remodl.VertexAILlama3Config().get_supported_openai_params(
                    model=model
                )
        elif request_type == "embeddings":
            return remodl.VertexAITextEmbeddingConfig().get_supported_openai_params()
    elif custom_llm_provider == "sagemaker":
        return remodl.SagemakerConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "aleph_alpha":
        return [
            "max_tokens",
            "stream",
            "top_p",
            "temperature",
            "presence_penalty",
            "frequency_penalty",
            "n",
            "stop",
        ]
    elif custom_llm_provider == "cloudflare":
        return remodl.CloudflareChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nlp_cloud":
        return remodl.NLPCloudConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "petals":
        return remodl.PetalsConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "deepinfra":
        return remodl.DeepInfraConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "perplexity":
        return remodl.PerplexityChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nscale":
        return remodl.NscaleConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "anyscale":
        return [
            "temperature",
            "top_p",
            "stream",
            "max_tokens",
            "stop",
            "frequency_penalty",
            "presence_penalty",
        ]
    elif custom_llm_provider == "watsonx":
        return remodl.IBMWatsonXChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "watsonx_text":
        return remodl.IBMWatsonXAIConfig().get_supported_openai_params(model=model)
    elif (
        custom_llm_provider == "custom_openai"
        or custom_llm_provider == "text-completion-openai"
    ):
        return remodl.OpenAITextCompletionConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "predibase":
        return remodl.PredibaseConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "voyage":
        return remodl.VoyageEmbeddingConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "infinity":
        return remodl.InfinityEmbeddingConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "triton":
        if request_type == "embeddings":
            return remodl.TritonEmbeddingConfig().get_supported_openai_params(
                model=model
            )
        else:
            return remodl.TritonConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "deepgram":
        if request_type == "transcription":
            return (
                remodl.DeepgramAudioTranscriptionConfig().get_supported_openai_params(
                    model=model
                )
            )
    elif custom_llm_provider == "elevenlabs":
        if request_type == "transcription":
            from remodl.llms.elevenlabs.audio_transcription.transformation import (
                ElevenLabsAudioTranscriptionConfig,
            )

            return ElevenLabsAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider in remodl._custom_providers:
        if request_type == "chat_completion":
            provider_config = remodl.ProviderConfigManager.get_provider_chat_config(
                model=model, provider=LlmProviders.CUSTOM
            )
            if provider_config:
                return provider_config.get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return None
        elif request_type == "transcription":
            return None

    return None
