# Before: weight download baked into the server

`server.py` downloads the "model weights" file from a hardcoded URL on startup. The source URL and all download logic live inside the server code.

Change the source (S3 to GCS, one bucket to another, local file to HuggingFace Hub) and you edit `server.py` and rebuild the image.

## Run it

No dependencies beyond the standard library.

```bash
python3 server.py
```

You'll see the weight download happen during startup:

```
[startup] Downloading weights from https://... 
[startup] Weights downloaded in 0.31s -> /tmp/weights.txt
[startup] Model loaded. Weights preview: these are fake model weights...
[ready] Inference server listening on port 8080
```

In another terminal, test the endpoint:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/predict
```

## The problem

The server image carries knowledge of where the weights live. On a real inference server this means:

- Cloud credentials baked into the image (or injected via env vars that the server code reads)
- A different team manages weight storage? They have to coordinate with whoever owns the server image.
- Move weights to a new bucket? Rebuild and redeploy the server.
- The server startup time includes the download. There is no way to pre-stage weights independently.

The [after/](../after/) folder shows a cleaner split.
