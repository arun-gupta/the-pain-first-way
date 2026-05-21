# Pain 7 example: the same traffic, three layers of improvement

A working demonstration of [Pain 7: My GPU sits at 30% but my bill says 100%](../../pains/07-gpu-underutilized.md). Same inference server, same simulated workload, three independent improvements applied one at a time. No GPU required.

## What's here

```
07-gpu-underutilized/
├── before/        # the typical way: sequential serving, wrong autoscaling signal
│   ├── server.py
│   └── README.md
└── after/         # three incremental fixes
    ├── server.py          # Step 1: concurrent batching, no infrastructure change
    ├── deployment.yaml    # Step 2: deploy with Prometheus scraping annotations
    ├── scaledobject.yaml  # Step 2: KEDA scales on inference_requests_in_flight
    ├── mig-config.yaml    # Step 3: MIG profiles via GPU Operator (requires real GPU)
    └── README.md
```

No GPU required. All GPU behavior is simulated with `time.sleep`. The cloud-native concepts are identical to a real vLLM deployment.

## The point of the diff

`before/server.py` processes requests sequentially — one at a time, GPU idle between them. Five concurrent requests take ~2.5s wall time. Kubernetes can't scale it on CPU because CPU stays at 5% even when the GPU queue is growing.

`after/server.py` processes up to `MAX_CONCURRENT` requests in parallel — five concurrent requests take ~0.5s wall time regardless of count. It also exposes `/metrics` with `inference_requests_in_flight` so KEDA can scale on actual GPU load rather than CPU.

`after/scaledobject.yaml` configures KEDA to watch `inference_requests_in_flight` and add replicas when it exceeds 3. `after/mig-config.yaml` shows how to partition a physical GPU into isolated slices so multiple workloads can share one card.

Each layer is independent. Step 1 is a one-line deployment change. Steps 2 and 3 add infrastructure only when you need it.

## Run it

- [`before/README.md`](before/README.md) — run with Python, send concurrent requests, observe serialization
- [`after/README.md`](after/README.md) — Step 1: run with Python, observe parallelism and metrics; Step 2: apply KEDA; Step 3: configure MIG

---

[← Back to Pain 7](../../pains/07-gpu-underutilized.md) · [Landscape](../../README.md) · [Examples index](../README.md)
