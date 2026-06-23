---
title: MarketInsights-AI
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# MarketInsights-AI

**Advanced Autonomous AI Agent for Market Research, Data Science, and Educational Analysis**

MarketInsights-AI is a professional-grade research agent designed for automated data gathering, sentiment analysis, and multi-source market reporting.

## 🚀 Key Features

- **Educational Research**: Optimized for gathering and summarizing data from multiple public sources (Wikipedia, News, Public Forums).
- **Sentiment Analysis**: Real-time analysis of market sentiment trends using state-of-the-art NLP models.
- **Robust Persistence**: Securely stores research data and logs locally with optional cloud synchronization.
- **Multi-Key High Availability**: Uses a failover system for API keys to ensure continuous research capabilities.
- **In-Built Text Splitting**: Intelligent processing of large datasets to maintain high-quality summaries.

## ⚖️ Financial Disclaimer

**IMPORTANT: This software is for EDUCATIONAL and RESEARCH purposes only.**
- It does NOT provide financial advice.
- It is NOT a trading platform.
- The authors are not responsible for any decisions made based on the data provided by this agent.
- Always perform your own due diligence.

## 🏛 Architecture

```
User
   │
   ▼
AI Orchestrator (cron_manager.py)
   │
   ├── Reasoning Engine (skills/reasoning/decision_engine.py)
   ├── Analysis Module (skills/analysis/)
   ├── Data Scrapers (skills/web_scraper.py)
   ├── Math & Metrics (skills/math/metrics.py)
   ├── API Proxy (api_proxy.py)
   └── Persistence Layer (persistence_manager.py)
```

## 📦 Deployment

MarketInsights-AI is designed to run efficiently on small server environments and is optimized for Hugging Face Docker Spaces.

```bash
docker-compose up --build
```

---
*Focus on Data. Analyze Risk. Learn Daily.*
