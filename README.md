---
title: Money Maker🤑
emoji: 🤑
colorFrom: green
colorTo: emerald
sdk: docker
pinned: false
---

# Money Maker🤑

**Advanced Autonomous AI Agent for Financial Intelligence, Sports Betting, and Crypto Trading**

Money Maker🤑 is a production-ready, autonomous AI agent designed to dominate markets through disciplined reasoning, rigorous risk management, and continuous self-improvement.

## 🚀 Key Features (Ultimate Version)

- **Seamless Small Server Execution**: Optimized for low-resource environments with local SQLite fallback for memory.
- **Self-Saving Memory**: Saves all its own memory and logs to a local Postgres/SQLite database without external dependencies (while still supporting optional Supabase sync).
- **Multi-Layer API Key System**: Every integrated service (Groq, HF, Google, Odds API, Reddit) uses a comma-separated multi-key rotation system for zero-downtime.
- **In-Built Text Splitting**: Intelligent recursive text splitter prevents LLM token limit errors during heavy data processing.
- **Reddit Sentiment Analysis**: Real-time market sentiment gathering from Reddit with automated multi-key rotation.

## 🏛 Production-Ready Architecture

```
User
   │
   ▼
AI Orchestrator (cron_manager.py)
   │
   ├── Reasoning Engine (skills/reasoning/decision_engine.py)
   ├── Risk Manager (skills/finance/risk_manager.py)
   ├── Sports Betting Module (skills/betting/)
   ├── Crypto Trading Module (skills/crypto/)
   ├── Math & Metrics (skills/math/metrics.py)
   ├── Self-Improvement (skills/analysis/self_improvement.py)
   ├── Reddit Sentiment (skills/analysis/reddit_sentiment.py)
   ├── Text Splitter (skills/analysis/text_splitter.py)
   ├── API Proxy (api_proxy.py)
   └── Self-Saving Database (persistence_manager.py)
```

## 🛠 Setup

### Multi-Key Configuration
Supply comma-separated pools for ALL services:
- `GROQ_API_KEYS=key1,key2...`
- `ODDS_API_KEYS=key1,key2...`
- `REDDIT_API_KEYS=key1,key2...`
- `HUGGINGFACE_API_KEYS=key1,key2...`

## 📦 Deployment

Deploy to **Hugging Face Docker Spaces**.

```bash
docker-compose up --build
```

---
*Built for the Year 2029. Focus on Positive EV. Manage Risk. Improve Daily.*
