# Money Maker🤑 - AI Agent (Root Enabled & Small Server Optimized)
ARG HERMES_AGENT_VERSION=latest
FROM nousresearch/hermes-agent:${HERMES_AGENT_VERSION}

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq sudo python3 python3-venv python3-pip \
    chromium libpq-dev sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && uv pip install --python /opt/hermes/.venv/bin/python --no-cache-dir \
        huggingface_hub hf_transfer jupyterlab tornado ipywidgets \
        psycopg2-binary apify-client litellm beautifulsoup4 requests \
        schedule numpy fastapi uvicorn \
    && printf 'hermes ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/hermes \
    && chmod 0440 /etc/sudoers.d/hermes

ENV MONEY_MAKER_APP_DIR=/opt/money-maker
RUN mkdir -p ${MONEY_MAKER_APP_DIR} && chown hermes:hermes ${MONEY_MAKER_APP_DIR}

COPY --chown=hermes:hermes . ${MONEY_MAKER_APP_DIR}/

RUN chmod +x ${MONEY_MAKER_APP_DIR}/*.sh ${MONEY_MAKER_APP_DIR}/*.py

RUN echo 'export PATH="/opt/hermes/.venv/bin:/opt/data/.local/bin:$PATH"' > /etc/profile.d/hermes-venv.sh

ENV HERMES_HOME=/opt/data \
    HUGGINGMES_APP_DIR=${MONEY_MAKER_APP_DIR} \
    PYTHONUNBUFFERED=1

EXPOSE 7861

# Switch to root for unrestricted access
USER root
WORKDIR /opt/money-maker

CMD ["/opt/money-maker/start.sh"]
