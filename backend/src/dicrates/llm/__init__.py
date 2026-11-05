"""The only module that talks to LLM providers (see docs/architecture.md → LLM layer).

* `factory.build_model` turns `LLM_MODEL` into a Pydantic AI model (the only
  place that imports provider code).
* `prompts` loads versioned prompt files (`prompts/<name>.v<N>.md`).
* `runner.LlmRunner` runs one structured-output task with retries and writes a
  text-free usage record (`call_log`).
"""
