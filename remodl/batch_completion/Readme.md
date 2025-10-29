# Implementation of `remodl.batch_completion`, `remodl.batch_completion_models`, `remodl.batch_completion_models_all_responses`

Doc: https://docs.remodl.ai/docs/completion/batching


LiteLLM Python SDK allows you to:
1. `remodl.batch_completion` Batch remodl.completion function for a given model.
2. `remodl.batch_completion_models` Send a request to multiple language models concurrently and return the response
    as soon as one of the models responds.
3. `remodl.batch_completion_models_all_responses` Send a request to multiple language models concurrently and return a list of responses
    from all models that respond.