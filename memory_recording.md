# Money Maker 🤑 - Engineering Memory

## Patterns & Solutions
- **Multi-Key LLM Failover**: Implemented a FastAPI proxy (`api_proxy.py`) using `litellm` that catches 4xx/5xx errors and rotates through a list of API keys in a pool. This ensures 24/7 reliability even on free-tier rate limits.
- **Persistence Handling**: SQLite initialization in v3.12+ can fail with `ProgrammingError` if multiple statements are passed to `execute()`. Always use `executescript()` or loop through individual statements.
- **Render Port Binding**: Render expects the web service to bind to `0.0.0.0` on the port specified by `$PORT` (default 10000). A Node.js `health-server.js` was used as the primary entry point to ensure the port is opened immediately while the heavier Python agent initializes.
- **Hugging Face Spaces Redirection**: For private spaces, `.hf.space` direct URLs often fail to authenticate correctly. The `health-server.js` detects these requests and redirects them to the canonical `huggingface.co/spaces` URL.

## Deployment Checklist
1. Ensure `GATEWAY_TOKEN` is set for dashboard and terminal access.
2. Provide at least one key for Groq, Google, or Hugging Face.
3. Configure `RENDER_EXTERNAL_URL` for the keep-alive service.
4. For persistent cross-deployment memory, provide a `POSTGRES_URL`.
