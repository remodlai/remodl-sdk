"""
Registry mapping the callback class string to the class type.

This is used to get the class type from the callback class string.

Example:
    "datadog" -> DataDogLogger
    "prometheus" -> PrometheusLogger
"""

from typing import Union

from remodl import _custom_logger_compatible_callbacks_literal
from remodl.integrations.agentops import AgentOps
from remodl.integrations.anthropic_cache_control_hook import AnthropicCacheControlHook
from remodl.integrations.argilla import ArgillaLogger
from remodl.integrations.azure_storage.azure_storage import AzureBlobStorageLogger
from remodl.integrations.bitbucket import BitBucketPromptManager
from remodl.integrations.gitlab import GitLabPromptManager
from remodl.integrations.braintrust_logging import BraintrustLogger
from remodl.integrations.datadog.datadog import DataDogLogger
from remodl.integrations.datadog.datadog_llm_obs import DataDogLLMObsLogger
from remodl.integrations.deepeval import DeepEvalLogger
from remodl.integrations.galileo import GalileoObserve
from remodl.integrations.gcs_bucket.gcs_bucket import GCSBucketLogger
from remodl.integrations.gcs_pubsub.pub_sub import GcsPubSubLogger
from remodl.integrations.humanloop import HumanloopLogger
from remodl.integrations.lago import LagoLogger
from remodl.integrations.langfuse.langfuse_prompt_management import (
    LangfusePromptManagement,
)
from remodl.integrations.langsmith import LangsmithLogger
from remodl.integrations.literal_ai import LiteralAILogger
from remodl.integrations.mlflow import MlflowLogger
from remodl.integrations.openmeter import OpenMeterLogger
from remodl.integrations.opentelemetry import OpenTelemetry
from remodl.integrations.opik.opik import OpikLogger
from remodl.integrations.posthog import PostHogLogger

try:
    from remodl_enterprise.integrations.prometheus import PrometheusLogger
except Exception:
    PrometheusLogger = None
from remodl.integrations.cloudzero.cloudzero import CloudZeroLogger
from remodl.integrations.dotprompt import DotpromptManager
from remodl.integrations.s3_v2 import S3Logger
from remodl.integrations.sqs import SQSLogger
from remodl.integrations.vector_store_integrations.vector_store_pre_call_hook import (
    VectorStorePreCallHook,
)
from remodl.proxy.hooks.dynamic_rate_limiter import _PROXY_DynamicRateLimitHandler
from remodl.proxy.hooks.dynamic_rate_limiter_v3 import _PROXY_DynamicRateLimitHandlerV3
from remodl.proxy.hooks.nova_task_routing import NovaTaskRoutingHook


class CustomLoggerRegistry:
    """
    Registry mapping the callback class string to the class type.
    """

    CALLBACK_CLASS_STR_TO_CLASS_TYPE = {
        "lago": LagoLogger,
        "openmeter": OpenMeterLogger,
        "braintrust": BraintrustLogger,
        "galileo": GalileoObserve,
        "langsmith": LangsmithLogger,
        "literalai": LiteralAILogger,
        "prometheus": PrometheusLogger,
        "datadog": DataDogLogger,
        "datadog_llm_observability": DataDogLLMObsLogger,
        "gcs_bucket": GCSBucketLogger,
        "opik": OpikLogger,
        "argilla": ArgillaLogger,
        "opentelemetry": OpenTelemetry,
        "azure_storage": AzureBlobStorageLogger,
        "humanloop": HumanloopLogger,
        # OTEL compatible loggers
        "logfire": OpenTelemetry,
        "arize": OpenTelemetry,
        "langfuse_otel": OpenTelemetry,
        "arize_phoenix": OpenTelemetry,
        "langtrace": OpenTelemetry,
        "mlflow": MlflowLogger,
        "langfuse": LangfusePromptManagement,
        "otel": OpenTelemetry,
        "gcs_pubsub": GcsPubSubLogger,
        "anthropic_cache_control_hook": AnthropicCacheControlHook,
        "agentops": AgentOps,
        "deepeval": DeepEvalLogger,
        "s3_v2": S3Logger,
        "aws_sqs": SQSLogger,
        "dynamic_rate_limiter": _PROXY_DynamicRateLimitHandler,
        "dynamic_rate_limiter_v3": _PROXY_DynamicRateLimitHandlerV3,
        "nova_task_router": NovaTaskRoutingHook,
        "vector_store_pre_call_hook": VectorStorePreCallHook,
        "dotprompt": DotpromptManager,
        "bitbucket": BitBucketPromptManager,
        "gitlab": GitLabPromptManager,
        "cloudzero": CloudZeroLogger,
        "posthog": PostHogLogger,
    }

    try:
        from remodl_enterprise.enterprise_callbacks.generic_api_callback import (
            GenericAPILogger,
        )
        from remodl_enterprise.enterprise_callbacks.pagerduty.pagerduty import (
            PagerDutyAlerting,
        )
        from remodl_enterprise.enterprise_callbacks.send_emails.resend_email import (
            ResendEmailLogger,
        )
        from remodl_enterprise.enterprise_callbacks.send_emails.smtp_email import (
            SMTPEmailLogger,
        )

        enterprise_loggers = {
            "pagerduty": PagerDutyAlerting,
            "generic_api": GenericAPILogger,
            "resend_email": ResendEmailLogger,
            "smtp_email": SMTPEmailLogger,
        }
        CALLBACK_CLASS_STR_TO_CLASS_TYPE.update(enterprise_loggers)
    except ImportError:
        pass  # enterprise not installed

    @classmethod
    def get_callback_str_from_class_type(cls, class_type: type) -> Union[str, None]:
        """
        Get the callback string from the class type.

        Args:
            class_type: The class type to find the string for

        Returns:
            str: The callback string, or None if not found
        """
        for (
            callback_str,
            callback_class,
        ) in cls.CALLBACK_CLASS_STR_TO_CLASS_TYPE.items():
            if callback_class == class_type:
                return callback_str
        return None

    @classmethod
    def get_all_callback_strs_from_class_type(cls, class_type: type) -> list[str]:
        """
        Get all callback strings that map to the same class type.
        Some class types (like OpenTelemetry) have multiple string mappings.

        Args:
            class_type: The class type to find all strings for

        Returns:
            list: List of callback strings that map to the class type
        """
        callback_strs: list[str] = []
        for (
            callback_str,
            callback_class,
        ) in cls.CALLBACK_CLASS_STR_TO_CLASS_TYPE.items():
            if callback_class == class_type:
                callback_strs.append(callback_str)
        return callback_strs

    @classmethod
    def get_class_type_for_custom_logger_name(
        cls,
        custom_logger_name: _custom_logger_compatible_callbacks_literal,
    ) -> type:
        """
        Get the class type for a given custom logger name
        """
        return cls.CALLBACK_CLASS_STR_TO_CLASS_TYPE[custom_logger_name]
