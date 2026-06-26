# Money Maker 🤑 - Agent Architecture Learnings

## Rebranding & Stealth
- Autonomous rebranding was achieved by patching the underlying `moneymaker_cli` package at runtime in the Dockerfile.
- This includes renaming UI tokens (`__HERMES_` -> `__MONEY_MAKER_`), Environment Variables (`HERMES_HOME` -> `MONEY_MAKER_HOME`), and Auth Headers (`X-Money Maker-Session-Token` -> `X-MoneyMaker-Session-Token`).
- Rebranding display strings prevents the agent from identifying as "Money Maker" in chat and logs.

## Dashboard
- A custom React-less high-fidelity dashboard was built from scratch using Tailwind CSS, Lucide icons, and Xterm.js.
- It bypasses the engine's built-in React UI completely while maintaining full API/WebSocket compatibility.

## Resilience
- Multi-layer API rotation handles 429 errors autonomously.
- Node.js health proxy manages Space initialization and "Invalid Host" header security.
- Autonomous cron management allows the agent to trigger its own wealth-generation tasks 24/7.
