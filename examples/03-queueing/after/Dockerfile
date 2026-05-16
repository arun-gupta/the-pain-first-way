# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app

# stdlib only -- no pip install needed.
COPY train.py .

# Run as a non-root user.
RUN useradd --create-home --shell /bin/bash trainer && chown -R trainer:trainer /app
USER trainer

# /checkpoints is mounted from the PVC at runtime.
VOLUME ["/checkpoints"]

CMD ["python", "train.py"]
