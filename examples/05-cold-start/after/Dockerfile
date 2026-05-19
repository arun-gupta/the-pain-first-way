# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app

# stdlib only -- no pip install needed.
# This image contains serving code only. No download logic, no credentials.
COPY server.py .
COPY downloader.py .
COPY weights.txt /weights-source/weights.txt

# Run as a non-root user.
RUN useradd --create-home --shell /bin/bash server && chown -R server:server /app
USER server

# /model is mounted from the shared emptyDir volume at runtime.
# The init container populates it before this container starts.
VOLUME ["/model"]

CMD ["python", "server.py"]
