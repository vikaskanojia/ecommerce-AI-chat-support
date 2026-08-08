"""Guardrailed Ecommerce Shopping Assistant -- Streamlit entrypoint.

Reads all tunable parameters from config.yaml. API keys come from environment
variables. Two sources, in priority order:
  1. Real environment variables / platform secrets (Streamlit Cloud's Settings ->
     Secrets, or HF Space secrets) -- always wins if set.
  2. A local .env file (see .env.example) -- for local development only, never
     committed to git (.env is in .gitignore).
"""

import os
import uuid

import streamlit as st
from dotenv import load_dotenv

# load_dotenv() never overrides a variable that's already set in the real
# environment, so platform secrets always take priority over a local .env --
# this line is a no-op in deployed environments that don't have a .env file.
load_dotenv()

from src.config_loader import load_config
from src.data import load_faq, load_products
from src.retrieval import build_embeddings, build_faq_index, build_product_index
from src.tools import build_tools
from src.agent import build_agent
from src.guardrails import load_nemo_rails
from src.observability import maybe_enable_tracing
from src.pipeline import make_guarded_chat_turn

cfg = load_config()

st.set_page_config(page_title=cfg["app"]["title"], page_icon=cfg["app"]["page_icon"], layout="centered")


# ---------------------------------------------------------------------------
# Startup: API keys, tracing, data, indexes, tools, agent, guardrails.
# Everything here is cached (st.cache_resource) so it only runs once per
# Space lifetime, not on every user message.
# ---------------------------------------------------------------------------

if not os.environ.get("GROQ_API_KEY"):
    st.error(
        "GROQ_API_KEY is not set. Add it as a secret in your Space settings "
        "(Settings -> Variables and secrets -> New secret)."
    )
    st.stop()

# NeMo's "openai" engine reads this env var name specifically, even though it's
# pointed at Groq via base_url in guardrails_config/config.yml -- no OpenAI
# account is involved, this is just the variable name that client checks.
os.environ["OPENAI_API_KEY"] = os.environ["GROQ_API_KEY"]

tracing_active = maybe_enable_tracing(
    cfg["observability"]["enable_langsmith"], cfg["observability"]["project_name"]
)

products_df = load_products(cfg["data"]["products_csv"])
faq_docs = load_faq(cfg["data"]["faq_json"])

embeddings = build_embeddings(cfg["retrieval"]["embedding_model"])
product_index = build_product_index(embeddings, products_df)
faq_index = build_faq_index(embeddings, faq_docs)

tools = build_tools(
    products_df, product_index, faq_index, faq_docs,
    cfg["retrieval"]["product_top_k"], cfg["retrieval"]["faq_top_k"],
)

agent = build_agent(
    tools, cfg["models"]["agent_model"], cfg["models"]["agent_temperature"], cfg["models"]["sdk_max_retries"]
)

rails = load_nemo_rails(cfg["guardrails"]["nemo_config_dir"]) if cfg["guardrails"]["enable_nemo_rails"] else None

guarded_chat_turn = make_guarded_chat_turn(cfg, agent, rails)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title(cfg["app"]["title"])
st.caption(cfg["app"]["subtitle"])

with st.sidebar:
    st.subheader("Configuration")
    st.markdown(f"**Agent model:** `{cfg['models']['agent_model']}`")
    st.markdown(f"**Safety classifier:** `{cfg['models']['safety_model']}`")
    st.markdown(f"**Catalog:** {len(products_df)} products, {products_df['category'].nunique()} categories")
    st.markdown(f"**FAQ entries:** {len(faq_docs)}")
    st.divider()
    st.markdown("**Guardrails**")
    st.markdown(f"- Safety classifier: {'✅ on' if cfg['guardrails']['enable_safety_classifier'] else '⬜ off'}")
    nemo_status = "✅ on" if rails is not None else ("⬜ off (config)" if not cfg["guardrails"]["enable_nemo_rails"] else "⚠️ failed to load")
    st.markdown(f"- NeMo policy rails: {nemo_status}")
    st.divider()
    st.markdown(f"**Observability:** {'✅ tracing to LangSmith' if tracing_active else '⬜ off'}")
    if tracing_active:
        st.caption(f"Project: `{cfg['observability']['project_name']}`")
    st.divider()
    show_trace = st.checkbox("Show which guardrail/tool handled each reply", value=True)
    if st.button("Reset conversation"):
        st.session_state.clear()
        st.rerun()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

for role, content, meta in st.session_state.history:
    with st.chat_message(role):
        st.write(content)
        if role == "assistant" and meta and show_trace:
            st.caption(meta)

question = st.chat_input("Ask about a product or a store policy...")
if question:
    st.session_state.history.append(("user", question, None))
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = guarded_chat_turn(question, st.session_state.thread_id)
        meta = f"blocked by: {result['blocked_by']}" if result["blocked_by"] else "no guardrail triggered"
        st.write(result["answer"])
        if show_trace:
            st.caption(meta)
    st.session_state.history.append(("assistant", result["answer"], meta))
