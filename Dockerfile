# Money Maker 🤑 - High Performance Autonomous Agent
ARG AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${AGENT_VERSION}

USER root

# Install minimal system dependencies for stability and basic shell utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq sudo python3 sqlite3 nodejs npm \
    && rm -rf /var/lib/apt/lists/*

ENV APP_DIR=/app
RUN mkdir -p ${APP_DIR} && chown hermes:hermes ${APP_DIR}

WORKDIR ${APP_DIR}

# No external python dependencies required.
# We use the optimized agent core provided in the base image.

# Setup sudo and vanity binary
RUN printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes \
    && ln -sf /opt/hermes/.venv/bin/hermes /usr/local/bin/money-maker

# Copy application files (rebranded custom logic)
COPY --chown=hermes:hermes . .

# Deep Rebranding Patch
# Rebrands the core agent engine to Money Maker 🤑
RUN set -ex; \
    PYTHON_EXE="/opt/hermes/.venv/bin/python"; \
    PKG_PATH=$($PYTHON_EXE -c "import hermes_cli; print(hermes_cli.__path__[0])"); \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Hermes Agent/Money Maker 🤑/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Nous Research/Money Maker/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/Hermes/MoneyMaker/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/hermes/moneymaker/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/__HERMES_/__MONEY_MAKER_/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/HERMES_HOME/MONEY_MAKER_HOME/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/HERMES_WEB_DIST/MM_WEB_DIST/g'; \
    find "$PKG_PATH" -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) -print0 | xargs -0 -r sed -i 's/X-Hermes-Session-Token/X-MoneyMaker-Session-Token/g'

RUN chmod +x *.sh *.py

# Space Configuration
ENV MONEY_MAKER_HOME=/opt/data \
    HERMES_HOME=/opt/data \
    MM_WEB_DIST=${APP_DIR}/money-maker-ui \
    HERMES_WEB_DIST=${APP_DIR}/money-maker-ui \
    PYTHONUNBUFFERED=1 \
    PORT=7860

EXPOSE 7860

USER root
CMD ["/app/start.sh"]
