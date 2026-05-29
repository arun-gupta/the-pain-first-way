# After: the same code, wrapped in a Dockerfile

`app.py` and `requirements.txt` are byte-for-byte identical to [`../before/`](../before/). The Dockerfile is the entire delta. It pins the Python version, installs the system library PyTorch needs, and bakes the model weights into the image at build time so the running container needs no network access.

## 0. Navigate to this directory

```bash
cd examples/F01-image/after
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (tested with 29+)

## 1. Build the image

```bash
bash build.sh
```

This builds `embedder:latest`. The build downloads `sentence-transformers/all-MiniLM-L6-v2` (~22 MB) into the image layer at build time. The first build takes a minute or two; subsequent builds use the Docker layer cache.

Expected output (abbreviated):

```
[+] Building ...
 => [1/8] FROM docker.io/library/python:3.11-slim
 => [2/8] RUN apt-get update && apt-get install -y --no-install-recommends libgomp1
 => [3/8] COPY requirements.txt .
 => [4/8] RUN pip install --no-cache-dir -r requirements.txt
 => [5/8] RUN python -c "from sentence_transformers import SentenceTransformer; ..."
 => [6/8] COPY app.py .
 => [7/8] RUN useradd --create-home --shell /bin/bash app ...
 => exporting to image

Built embedder:latest
```

## 2. Run the container

```bash
docker run -p 8000:8000 embedder:latest
```

Expected output:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

No model download on startup. The weights were baked into the image in step 1.

## 3. Test the endpoint

In another terminal:

```bash
curl -X POST http://localhost:8000/embed \
  -H 'content-type: application/json' \
  -d '{"text": "hello"}'
```

Expected output:

```json
{"text":"hello","dim":384,"embedding_preview":[0.028,0.123,-0.045,0.056,0.089,-0.012,0.034,0.078]}
```

(Embedding values are deterministic for a given model and input, but the exact preview depends on the model version.)

## 4. Clean up

Press `Ctrl+C` in the container terminal to stop it. If it is running in the background:

```bash
docker stop $(docker ps -q --filter ancestor=embedder:latest)
```

## What the Dockerfile declares

| Layer | What it pins |
|---|---|
| `FROM python:3.11-slim` | Python 3.11 exactly; no host Python leaks in |
| `RUN apt-get install -y libgomp1` | The OpenMP shared object PyTorch requires at runtime |
| `pip install -r requirements.txt` | All Python deps pinned against that one interpreter |
| `SentenceTransformer(...)` at build time | Model weights baked into the image layer; no network needed at runtime |
| Non-root `USER app` | Container runs without root privileges |

The image is the boundary. Inside, everything is declared. Outside no longer affects the runtime.

## What this maps to on a real GPU cluster

| This demo | Real ML service |
|---|---|
| `python:3.11-slim` base | CUDA base image (`nvcr.io/nvidia/pytorch:24.05-py3`) |
| `sentence-transformers/all-MiniLM-L6-v2` (22 MB) | 7B–70B model (7 GB–140 GB) |
| Model baked at build time | Model staged via init container at runtime (see [Pain S.01](../../../pains/S01-cold-start.md)) |
| `libgomp1` | CUDA toolkit, cuDNN, NCCL baked into GPU base image |
| `docker run -p 8000:8000` | Kubernetes Deployment with N replicas and GPU resource requests |

---

[← Back to Pain F.01](../../../pains/F01-model-works-locally.md) · [Landscape](../../../README.md) · [Examples index](../../README.md)
