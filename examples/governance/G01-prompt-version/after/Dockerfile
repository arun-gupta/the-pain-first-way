# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# stdlib only -- no pip install needed.
# No prompt baked in. The prompt is mounted from a ConfigMap at runtime.
COPY server.py .

RUN useradd --create-home --shell /bin/bash server && chown -R server:server /app
USER server

# /etc/prompt is mounted from the ConfigMap at runtime.
CMD ["python", "-u", "server.py"]
