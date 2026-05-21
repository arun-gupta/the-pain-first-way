# After: three incremental layers of improvement

Each step is independent. Step 1 requires no infrastructure. Steps 2 and 3 build on top of it.

## Step 1 — Swap the serving engine (no infrastructure change)

`server.py` uses `ThreadingMixIn` to handle multiple requests concurrently. Up to `MAX_CONCURRENT` (default 4) requests run in parallel. Send five concurrent requests and they overlap — total wall time stays near 0.5s instead of 2.5s.

```bash
cd examples/07-gpu-underutilized/after
python3 server.py
```

No dependencies beyond the standard library.

In another terminal, send five concurrent requests:

```bash
for i in $(seq 1 5); do curl -s localhost:8080/predict & done; wait
```

Watch the server terminal. Multiple requests start before the first one finishes.

Check the Prometheus metrics endpoint:

```bash
curl localhost:8080/metrics
```

Expected output:

```
# HELP inference_requests_in_flight Current concurrent inference requests
# TYPE inference_requests_in_flight gauge
inference_requests_in_flight 0
# HELP inference_requests_total Total inference requests served
# TYPE inference_requests_total counter
inference_requests_total 5
# HELP inference_tokens_per_second Estimated tokens per second
# TYPE inference_tokens_per_second gauge
inference_tokens_per_second 0
```

Set `MAX_CONCURRENT` via env var to change the concurrency limit:

```bash
MAX_CONCURRENT=2 python3 server.py
```

## Step 2 — Scale on the right signal

Requires a Kind cluster with [KEDA installed](https://keda.sh/docs/latest/deploy/) and Prometheus scraping the deployment.

Apply the deployment:

```bash
kubectl apply -f deployment.yaml
```

Apply the ScaledObject:

```bash
kubectl apply -f scaledobject.yaml
```

KEDA watches `inference_requests_in_flight` from Prometheus. When in-flight requests on any replica exceed 3, KEDA adds a replica — up to 5. When traffic drops, it scales back to 1.

Observe scaling:

```bash
kubectl get scaledobject inference-server-scaledobject
kubectl get hpa
```

This is the key difference from scaling on CPU: an inference server's CPU barely moves under load. The GPU queue fills and latency climbs while HPA watches CPU stay at 5% and does nothing. `inference_requests_in_flight` reflects actual GPU saturation.

## Step 3 — Share the GPU (informational)

`mig-config.yaml` is a ConfigMap that the NVIDIA GPU Operator reads to configure MIG profiles on GPU nodes. It divides one A100 80GB into three `3g.40gb` partitions. Three inference services share one physical GPU with hardware-enforced memory isolation.

This step requires a real GPU node (A100 or H100) with the NVIDIA GPU Operator installed. Apply it by labeling the node and creating the ConfigMap:

```bash
kubectl label node <your-gpu-node> nvidia.com/mig.config=all-3g.40gb
kubectl apply -f mig-config.yaml
```

Note: claiming a specific MIG slice from a pod requires DRA (Dynamic Resource Allocation). The default `nvidia.com/gpu: 1` counter cannot express slice type. See [issue #21](https://github.com/arun-gupta/the-pain-first-way/issues/21) for the full DRA pain.

---

[← Back to Pain 7](../../pains/07-gpu-underutilized.md) · [Landscape](../../README.md) · [Examples index](../README.md)
