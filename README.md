# Guarded E-Commerce AI Assistant

🛒 Search products & store policies — protected by active guardrails, real-time tracing,
and grounded catalog RAG.

A guarded, config-driven shopping/FAQ assistant implemented as a Streamlit app.

- **Agent**: uses the configured `agent_model` for tool-enabled QA and product lookup.
- **Guardrails**: a safety classifier plus optional NeMo rails protect responses.
- **Observability**: LangSmith tracing is enabled by default in `config.yaml` and
  attaches per-layer token usage and computed cost to each run tree.
- **Config-driven**: tune models, toggles, and pricing in `config.yaml` without code
  changes.

Product and FAQ data are static files in `data/` so the app starts quickly and
consistently.

## Deploy on Streamlit Community Cloud

### 1. Push this folder to a GitHub repo

Create a new repo (public or private) and upload everything in this folder to it --
keep the `src/`, `guardrails_config/`, `data/`, and `.streamlit/` subfolders intact.

### 2. Create the app

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Pick your repo, branch (`main`), and set **Main file path** to `app.py`
4. Click **Deploy**

### 3. Add secrets

In the app's **Settings → Secrets** (TOML format):

```toml
GROQ_API_KEY = "gsk_..."
LANGSMITH_API_KEY = "lsv2_..."  # optional: enable LangSmith tracing
```

| Secret | Required | Notes |
|---|---|---|
| `GROQ_API_KEY` | Yes | Free at [console.groq.com](https://console.groq.com) |
| `LANGSMITH_API_KEY` | No | Free at [smith.langchain.com](https://smith.langchain.com). When present and `observability.enable_langsmith` is true, traces are sent to LangSmith (project: `ecommerce-chatbot-prod`). |

Never put keys directly in `config.yaml` or any committed file -- use Streamlit Secrets for deployed apps. Saving triggers an automatic restart.

### 4. Watch it build

The app dashboard shows live build logs. First build installs `nemoguardrails`,
`sentence-transformers`, `torch`, etc., so expect a few minutes; later restarts are faster.

## Configuration

All runtime toggles live in `config.yaml`.

- `app` — UI title, subtitle, and page icon.
- `models` — agent, NeMo, and safety classifier model names and SDK retry caps.
- `retrieval` — embedding model and retrieval `top_k` settings for products/FAQ.
- `guardrails` — enable or disable the safety classifier and NeMo rails.
- `retry` — retry/backoff behavior for rate-limited calls.
- `observability` — `enable_langsmith` and `project_name` (defaults to `ecommerce-chatbot-prod`).
- `pricing` — per-token USD rates used to compute costs attached to traces.

Edit `config.yaml` for behavior changes; no source edits are required.

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your real GROQ_API_KEY (and optionally LANGSMITH_API_KEY)
streamlit run app.py
```

`.env` is read automatically on startup and is gitignored. Alternatively, export the secret environment variables in your shell before running.

Always keep secrets out of committed files: use `.env` (local) or Streamlit Secrets (deployed).

## Folder structure

```
.
├── app.py                    # Streamlit entrypoint
├── config.yaml                # all tunable parameters
├── .env.example                # template for local secrets (copy to .env, never commit .env)
├── requirements.txt
├── _generate_data.py          # one-time script that produced data/*.csv, data/*.json
├── data/
│   ├── ecommerce_products.csv
│   └── faq.json
├── guardrails_config/
│   ├── config.yml               # NeMo model config, pointed at Groq
│   └── rails.co                  # Colang policy flows
├── .streamlit/
│   └── config.toml               # theming
└── src/
    ├── config_loader.py
    ├── data.py
    ├── retrieval.py
    ├── tools.py
    ├── agent.py
    ├── guardrails.py
    ├── observability.py
    └── pipeline.py               # ties everything into one guarded_chat_turn
```

## Known limitations

- NeMo Guardrails' internal LLM call doesn't expose token usage through its public API,
  so that layer's cost isn't captured in traces (latency still is).
- Free-tier Groq rate limits (both per-minute and per-day) apply -- the retry logic backs
  off on a `429`, but a fully exhausted daily quota needs a wait for reset, not a retry.
- `nemoguardrails` is a heavier dependency; if it fails to install or load in a constrained
  environment, the app disables that layer and logs a warning rather than crashing.
- Streamlit Community Cloud free tier apps sleep after a period of inactivity and wake on
  the next visit (a short cold-start delay) -- normal free-tier behavior, not a bug.
- NeMo's policy check runs via `rails.generate_async()` in its own isolated event loop per
  call, not `nest_asyncio` -- on newer Streamlit builds (Starlette/anyio-based server),
  globally patching asyncio conflicts with Streamlit's own static-asset serving and breaks
  the UI itself, not just the guardrail call.
