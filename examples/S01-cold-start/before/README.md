# Before: weights downloaded on every cold start

`server.py` downloads the weights file on startup, before serving any requests. Every new server instance pays the full download cost before it can respond.

This is the natural starting point. The server downloads the weights file every time it starts up. In this demo the file is tiny and the download takes under a second. In production, a 70B FP16 model is ~140 GB; the same pattern means every new server instance waits 2-3 minutes just on the download before it can serve a single request.

The demo uses a local file copy to simulate the download (no network required). In production the source would be an S3 URL, a GCS path, or a HuggingFace repo ID — hardcoded in the server.

## Run it

```bash
cd examples/06-cold-start/before
```

No dependencies beyond the standard library.

```bash
python3 server.py
```

## Expected output

Startup:

```
[startup] Downloading weights from .../examples/06-cold-start/after/weights.txt ...
[startup] Weights downloaded in 0.00s -> /tmp/weights.txt
[startup] Model loaded. Weights preview: these are fake model weights...
[ready] Inference server listening on port 8080
[ready]   GET /health  -> liveness check
[ready]   GET /predict -> simulated inference
```

In another terminal:

```bash
$ curl localhost:8080/predict
prediction using model: [these are fake model weights
layer_0: 0.312 0.847 0.193 0.65...]
```

## The problem

Every time a new server instance starts, users wait for the download to complete before the first request can be served. In this demo the wait is milliseconds. In production it is minutes. The [`after/`](../after/) example shows how an init container stages weights into a shared volume before the server starts, so the server is ready as soon as the volume is mounted.
