FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/hhs
COPY . /opt/hhs
RUN python -m pip install --no-cache-dir -r requirements.txt -r deployment/pass153/requirements.txt
ENV PORT=7860
EXPOSE 7860
CMD ["python","-m","uvicorn","hhs_backend.pass153_server:app","--host","0.0.0.0","--port","7860"]
