# MarketInsights-AI - Educational Research Agent
ARG HERMES_AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${HERMES_AGENT_VERSION}

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq sudo python3 python3-venv python3-pip \
    chromium libpq-dev sqlite3 nodejs npm \
    && rm -rf /var/lib/apt/lists/*

ENV MARKET_INSIGHTS_APP_DIR=/opt/market-insights
RUN mkdir -p ${MARKET_INSIGHTS_APP_DIR} && chown hermes:hermes ${MARKET_INSIGHTS_APP_DIR}

WORKDIR ${MARKET_INSIGHTS_APP_DIR}

COPY requirements.txt .

RUN uv pip install --python /opt/hermes/.venv/bin/python --no-cache-dir -r requirements.txt \
    && printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes \
    && ln -s /opt/hermes/.venv/bin/hermes /usr/local/bin/market-insights

COPY --chown=hermes:hermes . .

RUN chmod +x *.sh *.py

RUN echo 'export PATH="/opt/hermes/.venv/bin:/opt/data/.local/bin:$PATH"' > /etc/profile.d/hermes-venv.sh

ENV HERMES_HOME=/opt/data \
    HUGGINGMES_APP_DIR=${MARKET_INSIGHTS_APP_DIR} \
    PYTHONUNBUFFERED=1 \
    PORT=10000

EXPOSE 10000

# Must remain root for s6-overlay to initialize and manage /run permissions
USER root
CMD ["/opt/market-insights/start.sh"]
