---
title: MarketInsights-AI (Enterprise)
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# MarketInsights-AI (Enterprise Edition)

**Advanced Autonomous AI Agent for Market Research and Data Science**

MarketInsights-AI is a high-performance research agent designed for 24/7 data gathering, sentiment analysis, and multi-source reporting. It is optimized for zero-downtime execution on free tier cloud platforms.

## 🚀 Deployment Guide

### 1. Render (Free Tier) - RECOMMENDED
- **Service Type**: Web Service
- **Runtime**: Docker
- **Build Command**: Leave empty (uses Dockerfile)
- **Start Command**: `./start.sh`
- **Port**: 10000 (Set in Env Vars as `PORT=10000`)
- **Root Directory**: Leave **BLANK** (default to repository root).
- **Environment Variables**:
    - `GATEWAY_TOKEN`: Your secret dashboard password.
    - `RENDER_EXTERNAL_URL`: Your service URL (e.g., `https://my-agent.onrender.com`).
    - `POSTGRES_URL`: (Optional) Link a Render Postgres instance for persistent memory.
    - `GROQ_API_KEYS`, `HUGGINGFACE_API_KEYS`, etc.

### 2. Hugging Face Spaces (Free)
- **SDK**: Docker
- **Hardware**: CPU Basic (Free)
- **Settings**: Add your API keys and `GATEWAY_TOKEN` to the "Variables and Secrets" section.
- **Auto-Update**: Pushing to your GitHub repository will automatically trigger a redeploy via the included GitHub Action.

### 3. Railway (Free Tier)
- **Deploy**: Connect your GitHub repository.
- **Port**: Automatically detected, or set `PORT=10000`.
- **Database**: Provision a Postgres instance on Railway and point `POSTGRES_URL` to the connection string.
- **Networking**: Ensure "Public Networking" is enabled for the web service.

## 🛠 Features

- **Multi-Key Failover**: Automatically rotates API keys when limits are hit.
- **Text Splitting**: In-built recursive character splitter to avoid LLM context errors.
- **Self-Saving Memory**: Uses local SQLite by default, with seamless Postgres fallback for permanent storage.
- **24/7 Keep-Alive**: Internal services prevent the agent from idling on free tier servers.
- **HITL Safety**: Human-in-the-loop confirmation required for destructive actions.

## ⚖️ Disclaimer

For Educational and Research purposes only. This agent does not provide financial advice.

---
*Built for the Year 2029. Focus on Data. Manage Risk. Stay Autonomous.*
