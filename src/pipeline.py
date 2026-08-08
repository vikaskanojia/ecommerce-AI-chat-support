"""Ties the guardrail layers, the agent, and observability together into one
guarded chatbot turn. This is the only function app.py calls per user message.
"""

from src.guardrails import invoke_with_retry, nemo_policy_check, safety_classifier_check
from src.observability import attach_usage, traceable


def make_guarded_chat_turn(cfg: dict, agent, rails):
    """Returns a guarded_chat_turn(user_message, thread_id) closure bound to this
    session's config, agent, and rails instance."""

    guardrails_cfg = cfg["guardrails"]
    models_cfg = cfg["models"]
    retry_cfg = cfg["retry"]
    pricing = cfg["pricing"]

    @traceable(run_type="chain", name="agent_call")
    def _run_agent(user_message: str, thread_id: str) -> str:
        from src.agent import SYSTEM_PROMPT

        def _call_agent():
            return agent.invoke(
                {"messages": [("system", SYSTEM_PROMPT), ("user", user_message)]},
                config={"configurable": {"thread_id": thread_id}},
            )

        result = invoke_with_retry(
            _call_agent, max_retries=retry_cfg["max_retries"], default_backoff=retry_cfg["default_backoff_seconds"]
        )
        last_message = result["messages"][-1]
        answer = last_message.content

        usage = getattr(last_message, "usage_metadata", None)
        if usage:
            attach_usage(models_cfg["agent_model"], usage.get("input_tokens", 0), usage.get("output_tokens", 0), pricing)

        return answer

    @traceable(run_type="llm", name="safety_classifier")
    def _check_safety(text: str) -> dict:
        verdict = safety_classifier_check(
            text, models_cfg["safety_model"], retry_cfg["max_retries"], retry_cfg["default_backoff_seconds"]
        )
        return verdict

    @traceable(run_type="chain", name="nemo_policy_check")
    def _check_policy(user_message: str):
        return nemo_policy_check(
            rails, user_message, retry_cfg["max_retries"], retry_cfg["default_backoff_seconds"]
        )

    @traceable(run_type="chain", name="guarded_chat_turn")
    def guarded_chat_turn(user_message: str, thread_id: str) -> dict:
        """Returns a dict: {"answer": str, "blocked_by": str or None}."""
        if guardrails_cfg["enable_safety_classifier"]:
            pre = _check_safety(user_message)
            if pre.get("violation") == 1:
                category = pre.get("category", "")
                if category and "off-topic" in category.lower():
                    answer = "I'm a store assistant for shopping and order questions -- I can't help with that, but I'm happy to help you find a product or answer a policy question!"
                elif category and "system" in category.lower():
                    answer = "I can't share internal system details or unpublished codes -- but I'm glad to help with products, orders, or store policies."
                else:
                    answer = f"I can't help with that ({category or 'policy violation'})."
                return {"answer": answer, "blocked_by": "safety_classifier (input)"}

        if guardrails_cfg["enable_nemo_rails"]:
            policy_refusal = _check_policy(user_message)
            if policy_refusal is not None:
                return {"answer": policy_refusal, "blocked_by": "nemo_policy_rail"}

        answer = _run_agent(user_message, thread_id)

        if guardrails_cfg["enable_safety_classifier"]:
            post = _check_safety(answer)
            if post.get("violation") == 1:
                return {
                    "answer": "I need to rephrase that -- could you ask your question a different way?",
                    "blocked_by": "safety_classifier (output)",
                }

        return {"answer": answer, "blocked_by": None}

    return guarded_chat_turn
