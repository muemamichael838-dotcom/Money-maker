# Money Maker🤑

**Advanced Autonomous AI Agent for Financial Intelligence, Sports Betting, and Crypto Trading**

Money Maker🤑 is a production-ready, autonomous AI agent designed to dominate markets through disciplined reasoning, rigorous risk management, and continuous self-improvement.

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
   ├── API Proxy (api_proxy.py)
   └── Database (Supabase/PostgreSQL via persistence_manager.py)
```

## 🚀 Core Capabilities

### 1. Market Analysis & Execution
- **Probability Estimation**: Calculates Expected Value (EV) and compares estimated probabilities against market implied odds.
- **Multi-Source Data**: Scrapes odds, prices, and sentiment from multiple redundant sources (Apify, Wikipedia, Custom Scrapers).
- **24/7 Operations**: Continuous market monitoring and automated execution.

### 2. Rigorous Risk Management
- **Dynamic Sizing**: Uses Fractional Kelly Criterion for optimal bankroll growth.
- **Hard Limits**: Implements daily loss limits and maximum drawdown protection.
- **Trade Validation**: Every action is cross-verified for positive EV and confidence thresholds.

### 3. Financial & Trading Intelligence
- **Technical Analysis**: Built-in RSI, MACD, EMA, SMA, and Bollinger Bands.
- **Betting Metrics**: CLV (Closing Line Value) tracking, Arbitrage detection, and Line movement analysis.

### 4. AI Reasoning & Self-Improvement
- **Explanatory Logic**: The agent explains the "Why" behind every decision.
- **Mistake Detection**: Automatically tracks prediction accuracy and detects recurring mistake patterns.
- **Autonomous Retraining**: Capable of triggering model retraining based on concept drift and performance metrics.

## 🛠 Setup

### Environment Variables

| Variable | Description |
| :--- | :--- |
| `GROQ_API_KEYS` | Pool of Groq keys for reasoning |
| `HUGGINGFACE_API_KEYS` | Pool of HF keys for analysis |
| `GOOGLE_API_KEYS` | Pool of Google/Gemini keys |
| `SUPABASE_URL` / `KEY` | Backend persistence |
| `ODDS_API_KEY` | Sports market data |
| `APIFY_TOKEN` | Web scraping power |

## 📦 Deployment

Optimized for **Hugging Face Docker Spaces** with root access and persistent volume sync.

```bash
docker-compose up --build
```

---
*Built for the Year 2029. Focus on Positive EV. Manage Risk. Improve Daily.*
