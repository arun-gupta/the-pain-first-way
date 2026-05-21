# After: two cloud-native layers on top of a batching server

The CN steps here (KEDA autoscaling, GPU partitioning) require a batching-aware server as their foundation. `server.py` is that foundation: it handles concurrent requests and exposes a `/metrics` endpoint in Prometheus format. The serving engine work — continuous batching, quantization, prefix caching — is covered in [`before/optimization-steps.md`](../before/optimization-steps.md). `server.py` simulates the result of that work so the CN layers can be demonstrated without a real GPU.

## Setup — Run the batching server

```bash
cd examples/07-gpu-underutilized/after
python3 server.py
```

No dependencies beyond the standard library.

Send five concurrent requests to populate the counters:

```bash
for i in $(seq 1 5); do curl -s localhost:8080/predict & done; wait
```

Expected output (order is non-deterministic — four requests acquire the semaphore immediately, the fifth waits for a slot):

```
prediction: total=4 elapsed=0.501s
prediction: total=3 elapsed=0.501s
prediction: total=2 elapsed=0.501s
prediction: total=1 elapsed=0.505s
prediction: total=5 elapsed=1.006s
```

`elapsed` is measured from when the request arrived, including any queue wait. Then check the metrics endpoint:

```bash
curl localhost:8080/metrics
```

Expected output (on a fresh server start after five requests):

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

`inference_requests_in_flight` is 0 because all five finished before you checked. To see it climb, lower the concurrency limit and send requests while they are still in flight:

```bash
MAX_CONCURRENT=2 python3 server.py
```

Send the same five concurrent requests. With only 2 slots, they batch into groups of 2, 2, 1:

```
prediction: total=1 elapsed=0.501s
prediction: total=2 elapsed=0.503s
prediction: total=3 elapsed=1.002s
prediction: total=4 elapsed=1.008s
prediction: total=5 elapsed=1.503s
```

The queue backing up — `inference_requests_in_flight` rising above 3 — is the signal Step 1 (KEDA) reacts to.

## Step 1 — Scale on the right signal

Requires a Kind cluster. Install KEDA:

```bash
kubectl apply --server-side -f https://github.com/kedacore/keda/releases/download/v2.16.0/keda-2.16.0.yaml
```

Wait for KEDA to be ready:

```bash
kubectl rollout status deployment/keda-operator -n keda
```

Apply the deployment:

```bash
kubectl apply -f deployment.yaml
```

Apply the ScaledObject:

```bash
kubectl apply -f scaledobject.yaml
```

KEDA watches `inference_requests_in_flight` from Prometheus. When in-flight requests on any replica exceed 3, KEDA adds a replica — up to 5. When traffic drops, it scales back to 1. Step 2 (MIG) is independent — it can be applied alongside this or separately.

Observe scaling:

```bash
kubectl get scaledobject inference-server-scaledobject
kubectl get hpa
```

This is the key difference from scaling on CPU: an inference server's CPU barely moves under load. The GPU queue fills and latency climbs while HPA watches CPU stay at 5% and does nothing. `inference_requests_in_flight` reflects actual GPU saturation.

## Step 2 — Share the GPU (informational)

`mig-config.yaml` is a ConfigMap that the NVIDIA GPU Operator reads to configure MIG profiles on GPU nodes. It divides one A100 80GB into three `3g.40gb` partitions. Three inference services share one physical GPU with hardware-enforced memory isolation.

This step requires a real GPU node (A100 or H100) with the NVIDIA GPU Operator installed. Apply it by labeling the node and creating the ConfigMap:

```bash
kubectl label node <your-gpu-node> nvidia.com/mig.config=all-3g.40gb
kubectl apply -f mig-config.yaml
```

Note: claiming a specific MIG slice from a pod requires DRA (Dynamic Resource Allocation). The default `nvidia.com/gpu: 1` counter cannot express slice type. See [issue #21](https://github.com/arun-gupta/the-pain-first-way/issues/21) for the full DRA pain.

---

[← Back to Pain 7](../../pains/07-gpu-underutilized.md) · [Landscape](../../README.md) · [Examples index](../README.md)
