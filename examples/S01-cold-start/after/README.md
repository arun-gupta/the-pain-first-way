# After: init container stages weights, server is unaware

`server.py` reads weights from `/model/weights.txt` and has no idea where they came from. `downloader.py` is the init container entrypoint: it stages the weights before the server starts. The server image contains serving code only.

## 0. Navigate to this directory

```bash
cd examples/06-cold-start/after
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (tested with 29+)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

## 1. Create a Kind cluster

If you already have a Kind cluster named `kind` from a previous example, you can skip this step.

```bash
kind create cluster --name kind 2>/dev/null || echo "Cluster already exists, reusing it."
```

## 2. Build and load the image

```bash
./build.sh
```

This builds the Docker image (which contains both `server.py` and `downloader.py`) and loads it directly into your Kind cluster. No registry needed.

## 3. Apply the manifest

```bash
kubectl apply -f init-container.yaml
```

This creates a PersistentVolumeClaim (a request for persistent storage) and a Pod. The init container stages weights to the PVC; the server reads from it.

## 4. Watch the init container run first

```bash
kubectl get pod inference-server -w
```

You'll see the pod move through `Init:0/1` before reaching `Running`:

```
NAME               READY   STATUS     RESTARTS   AGE
inference-server   0/1     Init:0/1   0          2s
inference-server   0/1     PodInitializing   0   4s
inference-server   1/1     Running    0          5s
```

Press `Ctrl+C` once the pod shows `Running` to return to the prompt.

The init container ran `downloader.py`, staged the weights to the shared volume, and exited. Only then did the server container start.

## 5. Check the init container logs

```bash
kubectl logs inference-server -c weight-downloader
```

```
[downloader] Staging weights from /weights-source/weights.txt to /model/weights.txt ...
[downloader] Done in 0.001s (142 bytes). Weights ready at /model/weights.txt.
```

## 6. Check the server logs

```bash
kubectl logs inference-server
```

```
[startup] Weights loaded from /model/weights.txt. Preview: these are fake model weights
layer_0: 0.312 0.847 0.193 0.65...
[startup] (No download happened here. The init container staged these weights.)
[ready] Inference server listening on port 8080
[ready]   GET /health  -> liveness check
[ready]   GET /predict -> simulated inference
```

The server never downloaded anything. It just read from the volume the init container prepared.

## 7. Test the endpoint

In one terminal, start the port-forward and leave it running:

```bash
kubectl port-forward pod/inference-server 8080:8080
```

Open a second terminal and run:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/predict
```

Expected output:

```
ok
prediction using model: [these are fake model weights
layer_0: 0.312 0.847 0.193 0.65...]
```

## 8. Simulate a pod restart

Delete and re-create the pod to simulate a cold start on a node that already has the weights cached on the PVC:

```bash
kubectl delete pod inference-server
kubectl apply -f init-container.yaml
```

Watch the init container logs again:

```bash
kubectl logs inference-server -c weight-downloader
```

```
[downloader] /model/weights.txt already present (142 bytes). Skipping download.
```

The weights were already on the PVC from the first run. The server was ready instantly. No download cost on restart.

## 9. Clean up

Press `Ctrl+C` in the port-forward terminal to stop it, then delete the pod and PVC:

```bash
kubectl delete pod inference-server
kubectl delete pvc model-weights
```

## What the manifest demonstrates

The key is the shared PVC and the ordering guarantee:

- `initContainers` run to completion before any container in `containers` starts.
- Both containers mount the same PVC at `/model`.
- The server starts with weights already present. It does not wait, poll, or retry.
- The PVC persists across pod restarts. On the first start, the init container downloads the weights. On subsequent restarts, the weights are already on the volume and the init container exits immediately.

## What this maps to on a real GPU cluster

| This demo | Real inference server |
|---|---|
| `python:3.11-slim` base | vLLM or TGI base image |
| `weights.txt` (142 bytes) | 70B FP16 weights (~140 GB) |
| `shutil.copy2` | `aws s3 sync`, `gsutil cp`, or HuggingFace hub download |
| `PVC (storageClassName: standard)` | PVC backed by local NVMe or shared storage (EFS, Filestore) |
| Swap `downloader.py` | Swap init container image or entrypoint args |

> **Scaling to multiple replicas:** This demo uses a single-node PVC (`ReadWriteOnce`). In production, use a `ReadWriteMany` PVC backed by a shared filesystem (EFS, Filestore, or similar) so all replicas (running instances of your model server) mount the same volume. The first init container downloads the weights once; every subsequent replica skips the download entirely.

---

[← Back to Pain S.01](../../pains/S01-cold-start.md) · [Landscape](../../README.md) · [Examples index](../README.md)
