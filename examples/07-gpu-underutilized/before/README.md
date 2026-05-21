# Before: sequential inference, GPU idle between requests

`server.py` processes one request at a time. Each `/predict` call sleeps for 0.5s (simulated GPU work). While it sleeps, every other request waits. Send five concurrent requests and they serialize — total wall time is ~2.5s instead of ~0.5s.

This is the pattern that produces ~30% GPU utilization at p50 load: the GPU is only working during those 0.5s windows. Between requests it sits idle.

## Run it

```bash
cd examples/07-gpu-underutilized/before
```

No dependencies beyond the standard library.

```bash
python3 server.py
```

## Observe the serialization

In another terminal, send five concurrent requests:

```bash
for i in $(seq 1 5); do curl -s localhost:8080/predict & done; wait
```

Watch the server terminal. You will see each request start only after the previous one finishes — they do not overlap.

## Expected server output

```
[ready] Sequential inference server listening on port 8080
[ready]   GET /health  -> liveness check
[ready]   GET /predict -> simulated inference (sequential)
[processing] request 1
[idle] waiting for next request
[processing] request 2
[idle] waiting for next request
[processing] request 3
[idle] waiting for next request
[processing] request 4
[idle] waiting for next request
[processing] request 5
[idle] waiting for next request
[utilization] GPU: ~30% (idle between requests)
```

## The problem

The server handles one request at a time. Concurrent traffic does not help — each request waits for the previous one to finish. Scaling out adds more replicas, but each replica runs the same sequential loop. Three replicas under the same load means three instances each at ~15% utilization. The bill triples; the throughput is unchanged.

The [`after/`](../after/) example shows two things: a batching-aware server that runs multiple requests in parallel (Step 1, no infrastructure change), and KEDA autoscaling on the right signal — `inference_requests_in_flight` rather than CPU (Step 2).
