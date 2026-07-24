FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r runtime/v22/requirements.txt && python scripts/build_v22_runtime.py
EXPOSE 8000
ENV JARVIS_ENV=staging
CMD ["uvicorn","runtime.v22.app.main:app","--host","0.0.0.0","--port","8000"]
