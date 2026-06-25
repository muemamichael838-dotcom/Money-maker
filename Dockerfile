# Money Maker 🤑 - High Performance Autonomous Agent
ARG HERMES_AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${HERMES_AGENT_VERSION}

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq sudo python3 python3-venv python3-pip \
    chromium libpq-dev sqlite3 nodejs npm \
    && rm -rf /var/lib/apt/lists/*

ENV APP_DIR=/app
RUN mkdir -p ${APP_DIR} && chown hermes:hermes ${APP_DIR}

WORKDIR ${APP_DIR}

# Copy requirements and install
COPY requirements.txt .
RUN /opt/hermes/.venv/bin/python -m pip install --no-cache-dir -r requirements.txt

# Setup sudo and aliases
RUN printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes \
    && ln -sf /opt/hermes/.venv/bin/hermes /usr/local/bin/money-maker

# Copy application files
COPY --chown=hermes:hermes . .

# Deep Rebranding Patch - Robust Dynamic Resolution
# This replaces "Hermes Agent" with "Money Maker 🤑" and "Nous Research" with "Money Maker"
# inside the installed library files to ensure the rebranding is deep and persistent.
RUN set -ex; \
    PYTHON_EXE="/opt/hermes/.venv/bin/python"; \
    [ -f "$PYTHON_EXE" ] || PYTHON_EXE="python3"; \
    PKG_PATH=$($PYTHON_EXE -c "import hermes_cli; print(hermes_cli.__path__[0])"); \
    echo "Rebranding package at $PKG_PATH"; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Hermes Agent/Money Maker 🤑/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Nous Research/Money Maker/g'

RUN chmod +x *.sh *.py

# Persistence and UI Config
ENV HERMES_HOME=/opt/data \
    HERMES_WEB_DIST=${APP_DIR}/money-maker-ui \
    PYTHONUNBUFFERED=1 \
    PORT=7860

EXPOSE 7860

# Space initialization requires root for some boot operations
USER root
CMD ["/app/start.sh"]
