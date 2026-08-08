# Guardrailed Ecommerce Shopping Assistant

A tool-using shopping/FAQ chatbot with two guardrail layers and full LangSmith
observability, deployed as a Streamlit app on **Streamlit Community Cloud**
(free, no Docker/paid plan needed).

- **Agent**: LangGraph, with tools for semantic product search, structured product
  filtering, and FAQ lookup, over a 100-product catalog + 16-entry FAQ document
- **Guardrails**: NeMo Guardrails (Colang policy rails) + a Groq-hosted, bring-your-own-policy
  safety classifier (`openai/gpt-oss-safeguard-20b`), both pre- and post-call
- **Observability**: every turn traces to LangSmith as one connected tree (classifier →
  policy check → agent → classifier), with real dollar cost attached per layer
- **Config-driven**: every model name, threshold, and toggle lives in `config.yaml` --
  no code changes needed to retune the deployment

All product/FAQ data is synthetic, generated once at build time (see `_generate_data.py`)
and committed as static files, so the app starts fast and consistently.

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
LANGSMITH_API_KEY = "lsv2_..."
```

| Secret | Required | Notes |
|---|---|---|
| `GROQ_API_KEY` | Yes | Free at [console.groq.com](https://console.groq.com) |
| `LANGSMITH_API_KEY` | No | Free at [smith.langchain.com](https://smith.langchain.com). Omit to run with observability off -- the app degrades gracefully. |

Never put keys directly in `config.yaml` or any committed file -- Secrets is the only
place they should live. Saving triggers an automatic restart.

### 4. Watch it build

The app dashboard shows live build logs. First build installs `nemoguardrails`,
`sentence-transformers`, `torch`, etc., so expect a few minutes; later restarts are faster.

## Configuration

Everything tunable lives in `config.yaml`:

- `models` -- which Groq-hosted models power the agent, NeMo, and the safety classifier
- `retrieval` -- embedding model, how many results each tool returns
- `guardrails` -- independently toggle the safety classifier and NeMo rails on/off
- `retry` -- backoff behavior on rate limits
- `observability` -- toggle LangSmith tracing, set the project name
- `pricing` -- per-token USD rates, used to compute real cost on traces

No code changes are needed to retune any of these -- edit `config.yaml`, commit, push.

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your real GROQ_API_KEY (and optionally LANGSMITH_API_KEY)
streamlit run app.py
```

`.env` is read automatically on startup and is gitignored -- it never gets committed.
If you'd rather not use a file, exporting the variable directly also works:

```bash
export GROQ_API_KEY=gsk_...
streamlit run app.py
```

Either way, **never** put real keys in `config.yaml` or any other committed file --
`.env` (local) and Streamlit Cloud's Settings → Secrets (deployed) are the only two
places they should live.

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
