FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HHS_REPOSITORY_ROOT=/app \
    HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0 \
    HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS=5 \
    HHS_PASS174_BOOT_TIMEOUT_SECONDS=12

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-litert-lm.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m py_compile \
      hhs_runtime/pass174/inheritance.py \
      hhs_runtime/pass174/runtime.py \
      hhs_backend/api/pass174_runtime_routes.py \
      hhs_backend/pass174_server.py \
    && test -f applications/pass174_visual_ide/index.html \
    && test -f applications/pass174_visual_ide/app.js

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import json,urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT','8000') + '/api/v1/pass174/deployment/status', timeout=4)); raise SystemExit(0 if data.get('ready') else 1)"

CMD ["sh", "deployment/pass174/start.sh"]
