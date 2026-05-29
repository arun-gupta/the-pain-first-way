# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

# Layer 2 of Pain 1: system libraries that PyTorch needs at runtime.
# Without libgomp1, sentence-transformers imports fail with:
#   OSError: libgomp.so.1: cannot open shared object file
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Layer 1 of Pain 1: Python deps pinned and installed against the one
# interpreter in this image. Same requirements.txt as the before/ folder.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 3 of Pain 1: bake the model weights into the image at build time.
# The running container needs no network access to load the model.
ENV HF_HOME=/app/.cache/huggingface
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Application code.
COPY app.py .

# Run as a non-root user.
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
