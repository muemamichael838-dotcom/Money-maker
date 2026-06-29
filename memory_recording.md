# Money Maker 🤑 - Agent Architecture Learnings

## Rebranding & Stealth
- Autonomous rebranding was achieved by patching the underlying `hermes_cli` package at runtime in the Dockerfile.
- This includes renaming UI tokens (`__HERMES_` -> `__MONEY_MAKER_`), Environment Variables (`HERMES_HOME` -> `MONEY_MAKER_HOME`), and Auth Headers (`X-Money Maker-Session-Token` -> `X-MoneyMaker-Session-Token`).
- Rebranding display strings prevents the agent from identifying as "Money Maker" in chat and logs.

## Dashboard
- A custom React-less high-fidelity dashboard was built from scratch using Tailwind CSS, Lucide icons, and Xterm.js.
- It bypasses the engine's built-in React UI completely while maintaining full API/WebSocket compatibility.

## Resilience
- Multi-layer API rotation handles 429 errors autonomously.
- Node.js health proxy manages Space initialization and "Invalid Host" header security.
- Autonomous cron management allows the agent to trigger its own wealth-generation tasks 24/7.

## API Configuration & Persistence
- The '/api/skills' endpoint was added to 'chat_bridge.py' to provide the UI with a list of available modular capabilities, resolving 404 errors in the Ops view.
- The '/api/settings' endpoint was implemented in 'chat_bridge.py' to allow the UI to persist Groq, Google, and Hugging Face API keys.
- Keys are saved to the persistence layer (SQLite/Postgres) under the 'api_settings' key, which is then picked up by 'api_proxy.py' for model routing.

## Mobile UX Optimization
- Dynamic visibility and fixed positioning were applied to the mobile chat input container to ensure it floats above the bottom navigation menu.
- A padding-bottom buffer was added to the chat messages container to prevent message bubbles from being obscured by the fixed input overlay.
