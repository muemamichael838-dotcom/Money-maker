# Contributing

Thanks for improving Money Maker 🤑.

## Local Checks

Run these before submitting changes:

```bash
bash -n start.sh
node --check health-server.js
python3 -m py_compile moneymaker-sync.py cloudflare-proxy-setup.py cloudflare-keepalive-setup.py
```

If Docker is available:

```bash
docker compose up --build
```

## Notes

- Keep the wrapper thin; prefer the official `nousresearch/moneymaker-agent` image for Money Maker itself.
- Avoid committing secrets or generated `/opt/data` state.
- Preserve Hugging Face Space metadata in `README.md`.
