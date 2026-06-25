# 🤑 Money Maker Agent

An autonomous AI agent designed for market insights, betting analysis, and automated money-making strategies. Based on the Money Maker 🤑 architecture, optimized for 24/7 operation on Hugging Face Docker Spaces.

## 🚀 Features

- **Multi-Layer AI Failover:** Support for Groq, Google (Gemini), Hugging Face, OpenAI, and Anthropic. Automatic key rotation and provider failover.
- **Persistent Memory:** Integrated with SQLite (local) and Postgres/Supabase (remote).
- **Advanced Skills:**
  - **Betting Analysis:** Gets real-time odds from Odds API.
  - **Market Intelligence:** Connected to Wikipedia and full web scraping capabilities (including Apify).
  - **Skill Creation:** Can generate its own Python skills at runtime.
- **24/7 Operation:** Built-in health server, keepalive loops, and Cloudflare integration to prevent hibernation.
- **Professional UI:** Professional dark-mode dashboard inspired by ChatGPT.
- **Root Access:** Full control over the Docker Space environment for advanced tasks.

## 🛠 Setup

1. Deploy to Hugging Face Docker Spaces.
2. Visit `/env-builder` to configure your API keys.
3. Use `MONEY_MAKER_ENV_BUNDLE` to save and restore your configuration securely.

## 🔒 Security & Privacy

Money Maker runs in your private Docker Space. All API keys and data are stored securely and never shared.

---
*Educational Tool. No Financial Advice. Always bet responsibly.*
