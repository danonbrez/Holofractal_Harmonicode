FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HHS_DISABLE_C_AUTOBUILD=1
WORKDIR /opt/hhs
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY . /opt/hhs
RUN python -m pip install --no-cache-dir -r requirements.txt -r deployment/pass153/requirements.txt
RUN make c-abi && test -f hhs_runtime/builds/libhhs_runtime.so
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/pass153/status')"
CMD ["python","-m","uvicorn","hhs_backend.pass153_server:app","--host","0.0.0.0","--port","8000"]
