# Money Maker 🤑 - High Performance Autonomous Agent
ARG AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${AGENT_VERSION}

USER root

# Install system dependencies
# We minimize system packages to save space and memory.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq sudo python3 python3-venv python3-pip \
    sqlite3 nodejs npm \
    && rm -rf /var/lib/apt/lists/*

ENV APP_DIR=/app
RUN mkdir -p ${APP_DIR} && chown hermes:hermes ${APP_DIR}

WORKDIR ${APP_DIR}

# Copy requirements
COPY requirements.txt .

# Install dependencies into the existing Hermes venv
# Using --prefer-binary to avoid memory-heavy compilation of packages like psycopg2-binary
RUN /opt/hermes/.venv/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/hermes/.venv/bin/python -m pip install --no-cache-dir --prefer-binary -r requirements.txt

# Setup sudo and vanity alias
RUN printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes \
    && ln -sf /opt/hermes/.venv/bin/hermes /usr/local/bin/money-maker

# Copy application files
COPY --chown=hermes:hermes . .

# Deep Rebranding Patch - Surgical & Comprehensive
RUN set -ex; \
    PYTHON_EXE="/opt/hermes/.venv/bin/python"; \
    PKG_PATH=$($PYTHON_EXE -c "import hermes_cli; print(hermes_cli.__path__[0])"); \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Hermes Agent/Money Maker 🤑/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Nous Research/Money Maker/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Hermes/MoneyMaker/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/hermes/moneymaker/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/__HERMES_/__MONEY_MAKER_/g'

RUN chmod +x *.sh *.py

# Persistence and UI Config
ENV MONEY_MAKER_HOME=/opt/data \
    HERMES_HOME=/opt/data \
    MM_WEB_DIST=${APP_DIR}/money-maker-ui \
    HERMES_WEB_DIST=${APP_DIR}/money-maker-ui \
    PYTHONUNBUFFERED=1 \
    PORT=7860

EXPOSE 7860

# Re-run as root for space init
USER root
CMD ["/app/start.sh"]
