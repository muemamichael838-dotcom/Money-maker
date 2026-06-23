# Money Maker🤑 - AI Agent for Financial Intelligence & Automation
# Based on HuggingMes/Hermes Agent

ARG HERMES_AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${HERMES_AGENT_VERSION}

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    jq \
    sudo \
    python3 \
    python3-venv \
    python3-pip \
    chromium \
    dbus \
    dbus-x11 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgbm1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxkbcommon0 \
    libx11-6 \
    libxext6 \
    libxfixes3 \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto-color-emoji \
    libpq-dev \
    && (apt-get install -y --no-install-recommends libasound2 2>/dev/null \
        || apt-get install -y --no-install-recommends libasound2t64 2>/dev/null \
        || true) \
    && rm -rf /var/lib/apt/lists/* \
    && uv pip install schedule  --python /opt/hermes/.venv/bin/python --no-cache-dir \
        huggingface_hub \
        hf_transfer \
        "jupyterlab>=4.0,<5" \
        "tornado>=6.4" \
        "ipywidgets>=8.1" \
        supabase \
        psycopg2-binary \
        apify-client \
        litellm \
        beautifulsoup4 \
        requests \
    && printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes \
    && /usr/sbin/visudo -cf /etc/sudoers.d/hermes

ENV MONEY_MAKER_APP_DIR=/opt/money-maker
RUN mkdir -p ${MONEY_MAKER_APP_DIR} && chown hermes:hermes ${MONEY_MAKER_APP_DIR}

COPY --chown=hermes:hermes start.sh ${MONEY_MAKER_APP_DIR}/start.sh
COPY --chown=hermes:hermes health-server.js ${MONEY_MAKER_APP_DIR}/health-server.js
COPY --chown=hermes:hermes hermes-sync.py ${MONEY_MAKER_APP_DIR}/hermes-sync.py
COPY --chown=hermes:hermes cloudflare-proxy-setup.py ${MONEY_MAKER_APP_DIR}/cloudflare-proxy-setup.py
COPY --chown=hermes:hermes cloudflare-keepalive-setup.py ${MONEY_MAKER_APP_DIR}/cloudflare-keepalive-setup.py
COPY --chown=hermes:hermes env-builder.html ${MONEY_MAKER_APP_DIR}/env-builder.html
COPY --chown=hermes:hermes env-builder.js ${MONEY_MAKER_APP_DIR}/env-builder.js

RUN chmod +x \
    ${MONEY_MAKER_APP_DIR}/start.sh \
    ${MONEY_MAKER_APP_DIR}/hermes-sync.py \
    ${MONEY_MAKER_APP_DIR}/cloudflare-proxy-setup.py \
    ${MONEY_MAKER_APP_DIR}/cloudflare-keepalive-setup.py

RUN python3 - <<'PY'
import sys
try:
    from pathlib import Path
    p = Path("/opt/hermes/hermes_cli/kanban_db.py")
    if p.exists():
        src = p.read_text(encoding="utf-8", errors="replace")
        if "# money-maker: idempotent-alter" not in src:
            old = '    conn.execute(\n        "ALTER TABLE tasks ADD COLUMN consecutive_failures "\n        "INTEGER NOT NULL DEFAULT 0"\n    )'
            new = '    try:  # money-maker: idempotent-alter\n        conn.execute(\n            "ALTER TABLE tasks ADD COLUMN consecutive_failures "\n            "INTEGER NOT NULL DEFAULT 0"\n        )\n    except Exception:\n        pass'
            p.write_text(src.replace(old, new), encoding="utf-8")
except Exception:
    pass
PY

RUN echo 'export PATH="/opt/hermes/.venv/bin:/opt/data/.local/bin:$PATH"' \
    > /etc/profile.d/hermes-venv.sh

ENV HERMES_HOME=/opt/data \
    HUGGINGMES_APP_DIR=${MONEY_MAKER_APP_DIR} \
    HERMES_AGENT_VERSION=${HERMES_AGENT_VERSION} \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

EXPOSE 7861

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD curl -fsS http://localhost:7861/health || (false)

CMD ["/opt/money-maker/start.sh"]
