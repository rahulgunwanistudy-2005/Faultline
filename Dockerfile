FROM python:3.13.5-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt ./
COPY apps/api/requirements.txt apps/api/requirements.txt
COPY packages/faultline_core packages/faultline_core
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m pip check \
    && groupadd --system faultline \
    && useradd --system --gid faultline --home-dir /app faultline

COPY --chown=faultline:faultline apps/api apps/api
COPY --chown=faultline:faultline apps/web-static apps/web-static
COPY --chown=faultline:faultline data data
COPY --chown=faultline:faultline docs docs
COPY --chown=faultline:faultline scripts scripts
COPY --chown=faultline:faultline start.sh start.sh

USER faultline
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/health', timeout=3).read()"

CMD ["./start.sh"]
