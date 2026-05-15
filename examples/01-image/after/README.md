# After: the cloud native way

The same `app.py` and `requirements.txt` as [`../before/`](../before/), wrapped in a Dockerfile. The image is the deployment artifact.

## Build and run

```bash
bash build.sh
docker run -p 8000:8000 embedder:latest
```

```bash
curl -X POST http://localhost:8000/embed \
  -H 'content-type: application/json' \
  -d '{"text": "hello"}'
```

## What the Dockerfile declares

Three things, mapping to Pain 1's three layers of "what's actually happening":

1. **Python and OS.** `FROM python:3.11-slim` pins the runtime. There is one Python in this container.
2. **System libraries.** `RUN apt-get install -y libgomp1` makes the OpenMP shared object part of the image. PyTorch's `dlopen` finds it because the file declared it.
3. **Python packages and model weights.** `pip install -r requirements.txt` runs inside the image with that pinned Python. The `RUN python -c "...SentenceTransformer(...)"` step downloads the model at build time so the runtime container doesn't need network access for it.

The image is the boundary. Inside, everything is declared. Outside no longer affects the runtime.

## Push to GHCR

```bash
docker login ghcr.io -u <your-github-username> -p <PAT-with-write-packages>
bash build.sh --push
```

`build.sh --push` tags as `ghcr.io/<GHCR_USERNAME>/embedder:latest` and pushes. Set `GHCR_USERNAME` if you're not the default.

## Why bake the model at build time

Pain 1 is about packaging everything together. Baking the 22MB MiniLM is the strictest version of that. The running container needs no network for the model. For multi-gigabyte LLMs, you'd download at runtime from a PVC or model registry; see [Pain 5: Cold start](../../pains/05-cold-start.md).
