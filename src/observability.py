"""LangSmith tracing setup. Entirely optional -- if disabled via config, or if no
LANGSMITH_API_KEY is present, tracing is silently skipped and everything else in the
app still works. The @traceable decorator degrades to a no-op if langsmith isn't
importable at all.
"""

import os


def maybe_enable_tracing(enabled: bool, project_name: str) -> bool:
    """Sets tracing env vars if enabled and a key is available. Returns whether
    tracing actually ended up active, so the UI can show accurate status."""
    if not enabled:
        return False
    if not os.environ.get("LANGSMITH_API_KEY"):
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = project_name
    os.environ["LANGSMITH_PROJECT"] = project_name
    return True


try:
    from langsmith import get_current_run_tree, traceable
except ImportError:
    def traceable(*args, **kwargs):
        """No-op fallback if langsmith isn't installed -- lets the rest of the app
        run unmodified rather than crashing on a missing optional dependency."""
        def decorator(fn):
            return fn
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator

    def get_current_run_tree():
        return None


def attach_usage(model: str, input_tokens: int, output_tokens: int, pricing: dict):
    """Attaches token usage + computed cost to the currently active trace span, if any."""
    run = get_current_run_tree()
    if run is None:
        return
    rates = pricing.get(model, {"input_per_million": 0, "output_per_million": 0})
    input_cost = input_tokens * rates["input_per_million"] / 1_000_000
    output_cost = output_tokens * rates["output_per_million"] / 1_000_000
    try:
        run.set(usage_metadata={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
        })
    except Exception:
        pass  # observability is best-effort -- never let it break the actual response
