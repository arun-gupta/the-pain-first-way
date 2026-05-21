# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# stdlib only -- no pip install needed.
# No credentials. No source URL. This image contains serving and download code only.
COPY server.py .
COPY downloader.py .
COPY weights.txt /weights-source/weights.txt

RUN useradd --create-home --shell /bin/bash server && chown -R server:server /app
USER server

# /model is mounted from the shared volume at runtime.
# The init container populates it before this container starts.
VOLUME ["/model"]

CMD ["python", "-u", "server.py"]
