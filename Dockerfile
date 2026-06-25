# Money Maker 🤑 - High Performance Autonomous Agent
ARG HERMES_AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${HERMES_AGENT_VERSION}

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq sudo python3 python3-venv python3-pip \
    chromium libpq-dev sqlite3 nodejs npm \
    && rm -rf /var/lib/apt/lists/*

ENV APP_DIR=/app
RUN mkdir -p ${APP_DIR} && chown hermes:hermes ${APP_DIR}

WORKDIR ${APP_DIR}

COPY requirements.txt .

# Install dependencies into the existing Hermes venv
RUN uv pip install --python /opt/hermes/.venv/bin/python --no-cache-dir -r requirements.txt

# Grant hermes user root privileges (Sudo)
RUN printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes \
    && ln -s /opt/hermes/.venv/bin/hermes /usr/local/bin/money-maker

# Copy application files
COPY --chown=hermes:hermes . .

# Deep Rebranding Patch
RUN /opt/hermes/.venv/bin/python -c " \
import os, re; \
base_path = '/opt/hermes/.venv/lib/python3.12/site-packages/hermes_cli'; \
for root, dirs, files in os.walk(base_path): \
    for f in files: \
        if f.endswith(('.py', '.js')): \
            p = os.path.join(root, f); \
            with open(p, 'r', errors='ignore') as fh: c = fh.read(); \
            new_c = c.replace('Hermes Agent', 'Money Maker 🤑').replace('Nous Research', 'Money Maker'); \
            if new_c != c: \
                with open(p, 'w') as fh: fh.write(new_c) \
"

RUN chmod +x *.sh *.py

# Environment setup
ENV HERMES_HOME=/opt/data \
    HERMES_WEB_DIST=${APP_DIR}/money-maker-ui \
    PYTHONUNBUFFERED=1 \
    PORT=7860

EXPOSE 7860

# Re-run root for space init
USER root
CMD ["/app/start.sh"]
