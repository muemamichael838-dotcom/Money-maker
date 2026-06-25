---
title: MarketInsights-AI (Enterprise)
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# MarketInsights-AI (Enterprise Edition)

**Privacy-First, Human-in-the-Loop AI Agent for Research and Analysis**

MarketInsights-AI is an enterprise-grade autonomous agent built for secure data gathering, research, and technical analysis. It prioritizes safety, transparency, and human oversight.

## 🛡 Enterprise Features

- **Human-in-the-Loop (HITL)**: Crucial destructive actions (like deleting skills or executing shell commands) are paused until a human provides explicit confirmation.
- **Privacy-First Architecture**: Runs entirely within your VPC/Space. Supports local SQLite/Postgres for complete data sovereignty.
- **Non-Root Execution**: Hardened security posture running as a restricted user to comply with enterprise safety standards.
- **Audit Logging**: Every decision and reasoning step is recorded with deep transparency in a persistent database.
- **Multi-Key Redundancy**: Zero-downtime operations with automatic rotation across multiple LLM and Data providers.

## ⚖️ Compliance & Safety

- **Manual Approval Required**: Skill deletion and core system changes require human confirmation.
- **No Financial Advice**: Purely for educational and research purposes.
- **Sandboxed Execution**: Designed for restricted environments with limited system-level access.

## 🏛 Architecture

```
User ↔ Human-in-the-Loop Gate
   │
   ▼
AI Orchestrator
   │
   ├── Safety Engine (Reasoning + HITL)
   ├── Analysis Module
   ├── Multi-Source Data
   └── Secure Persistence
```

## 📦 Enterprise Deployment

Optimized for **Hugging Face Enterprise** and Docker Spaces.

```bash
docker-compose up --build
```

---
*Built for Security. Managed by Humans. Powered by AI.*

## 🚀 Deployment Guide

### 1. Hugging Face Spaces (Free/Enterprise)
- **SDK**: Docker
- **Hardware**: CPU Basic (Free) or better.
- **Secrets**: Add `GATEWAY_TOKEN`, `HF_TOKEN`, and your API key pools.
- **Auto-Sync**: Use the provided GitHub Action `.github/workflows/sync-to-huggingface.yml`.

### 2. Render (Free Tier)
- **Root Directory**: Leave this **BLANK** (default to repository root).
- **Service Type**: Web Service
- **Runtime**: Docker
- **Port**: 10000
- **Database**: Create a Render Postgres instance and link it via `POSTGRES_URL`.
- **Keep-Alive**: The agent includes an internal `render_keepalive.py` that pings itself to prevent idling.
- **Environment Variables**: Add `RENDER_EXTERNAL_URL` (your app's URL) to enable the keep-alive service.

### 3. Railway (Free Tier)
- **Deploy**: Connect your GitHub repository.
- **Runtime**: Automatically detects Dockerfile.
- **Port**: Automatically detected or set `PORT=10000`.
- **Database**: Use Railway's Postgres plugin and link `DATABASE_URL` to `POSTGRES_URL`.
- **Persistence**: Railway free tier volumes are ephemeral; ensure `POSTGRES_URL` is set for permanent storage.

---
*Created for the elite analysts of 2029. Focus on Data. Manage Risk. Stay Compliant.*
