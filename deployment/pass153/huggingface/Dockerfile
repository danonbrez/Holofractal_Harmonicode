FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HHS_DISABLE_C_AUTOBUILD=1
WORKDIR /opt/hhs
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY . /opt/hhs
RUN python -m pip install --no-cache-dir -r requirements.txt -r deployment/pass153/requirements.txt
RUN make c-abi && test -f hhs_runtime/builds/libhhs_runtime.so
ENV PORT=7860
EXPOSE 7860
CMD ["python","-m","uvicorn","hhs_backend.pass153_server:app","--host","0.0.0.0","--port","7860"]
