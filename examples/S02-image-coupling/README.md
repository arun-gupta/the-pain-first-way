# Example 07: Server image coupling

A working demonstration of [Pain S.02: My server image is coupled to its config and secrets](../../pains/S02-server-image-coupling.md).

## The point of the diff

`before/server.py` hardcodes the weights source URL and credentials as constants. Any operational change -- rotating a key, moving to a new bucket, switching environments -- means editing the file and rebuilding the image.

`after/server.py` is serving code only. Source URL and credentials never enter the image; they are injected at runtime from a ConfigMap and a Secret. The server image is identical across every environment.

## What's here

```
before/
  server.py       # serving + download with hardcoded source URL and credentials
  weights.txt     # fake model weights used by the demo

after/
  server.py       # serving code only
  downloader.py   # init container -- reads source URL and credentials from env vars
  Dockerfile
  build.sh
  configmap.yaml  # WEIGHTS_SOURCE
  secret.yaml     # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
  pod.yaml        # PVC + init container + server container
  weights.txt     # fake model weights bundled into the init container image
```

## Run it

- [`before/README.md`](before/README.md) -- run bare with Python, observe the hardcoded source URL and credentials on every startup
- [`after/README.md`](after/README.md) -- build, apply, then simulate a key rotation and source change without rebuilding the image

---

[← Back to Pain S.02](../../pains/S02-server-image-coupling.md) · [Examples index](../README.md)
