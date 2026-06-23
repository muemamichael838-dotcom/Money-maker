# Money Maker🤑

**Professional AI Agent for Financial Intelligence & Automation**

Money Maker🤑 is a high-performance AI agent built for 24/7 financial operations, market analysis, and automated decision-making. It leverages a multi-layer AI infrastructure and a professional dashboard for real-time monitoring and control.

## 🚀 Features

- **Multi-Layer API Key System**: Support for multiple API keys across Groq, Hugging Face, Google, OpenAI, and Anthropic with automatic rotation and failover via `api_proxy.py`.
- **Persistent Memory & Logs**: Deep integration with Supabase and Postgres for long-term data retention and auditability.
- **Advanced Skills**:
    - **Market Odds**: Real-time sports betting odds via The Odds API.
    - **Web Scraping**: Redundant scraping system with Apify integration.
    - **Wikipedia**: Direct access to global knowledge.
    - **Skill Creator**: Ability to generate and deploy new skills on the fly.
- **Professional UI**: ChatGPT-inspired Obsidian Pulse aesthetic with real-time logs, memory management, and market dashboards.
- **24/7 Autonomy**: Automated cron management, self-healing runtime, and Cloudflare keep-alive integration.
- **Secure & Private**: Root access within Docker Space, encrypted API key storage, and private dataset backups.

## 🛠 Setup

### Environment Variables

| Variable | Description |
| :--- | :--- |
| `GATEWAY_TOKEN` | Auth token for dashboard access |
| `HF_TOKEN` | Hugging Face token with write access for backups |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase API key |
| `POSTGRES_URL` | Postgres connection string |
| `ODDS_API_KEY` | API key for the-odds-api.com |
| `APIFY_TOKEN` | Token for Apify scraping tasks |
| `GROQ_API_KEYS` | Comma-separated pool of Groq keys |
| `HUGGINGFACE_API_KEYS` | Comma-separated pool of HF keys |
| `GOOGLE_API_KEYS` | Comma-separated pool of Google/Gemini keys |

## 📦 Deployment

Deploy directly to **Hugging Face Docker Spaces**. The `Dockerfile` is pre-configured for root access and 24/7 operation.

```bash
# Local development
docker-compose up --build
```

---
*Created for the elite traders and automation engineers of 2029.*
