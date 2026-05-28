# Pain O.01 example: the same traffic, two layers of improvement

A working demonstration of [Pain O.01: My GPU sits at 30% but my bill says 100%](../../pains/O01-gpu-underutilized.md). Same inference server, same simulated workload: pre-CN serving-engine optimizations in `before/`, then two independent CN layers in `after/`. No GPU required.

## What's here

```
08-gpu-underutilized/
├── before/
│   ├── server.py    # naive sequential server — the problem
│   └── README.md    # sequential server demo + full pre-CN optimization path (ollama & vLLM)
└── after/           # CN layers on top of a batching server
    ├── server.py               # batching server with /metrics endpoint (foundation for CN steps)
    ├── deployment.yaml         # Kubernetes deployment with Prometheus scrape annotations
    ├── hpa-cpu.yaml            # CPU-based HPA — shows it misses the signal (CPU stays at ~4%)
    ├── scaledobject.yaml       # Step 1: KEDA scales on inference_requests_in_flight instead
    ├── mig-config.yaml         # Step 2: MIG profiles via GPU Operator (requires real GPU)
    └── README.md
```

No GPU required. All GPU behavior is simulated with `time.sleep`. The cloud-native concepts are identical to a real vLLM deployment.

## The point of the diff

`before/server.py` shows the problem: requests process one at a time, GPU idle between them. Five concurrent requests take ~2.5s wall time. CPU stays at 5% so Kubernetes HPA never triggers.

`before/README.md` shows what ML practitioners do first — before touching infrastructure. Two tracks: Mac path using ollama (no GPU required — runnable today on Apple Silicon) and GPU path using vLLM (production reference). Covers continuous batching, quantization, prefix caching, speculative decoding, sequence packing, and prefill/decode disaggregation.

`after/server.py` simulates a batching-aware engine: up to `MAX_CONCURRENT` requests run in parallel, five concurrent requests take ~0.5s regardless of count, and `/metrics` exposes `inference_requests_in_flight` so the autoscaler watches the right signal.

`after/hpa-cpu.yaml` is a CPU-based HPA that demonstrates the failure mode: CPU stays at ~4% under inference load, so the HPA never triggers. `after/scaledobject.yaml` replaces it with a KEDA ScaledObject that scales on `inference_requests_in_flight` instead — the signal that actually reflects GPU saturation. `after/mig-config.yaml` shows how to partition a physical GPU into isolated slices via the GPU Operator so multiple workloads can share one card.

Each layer is independent. The serving-engine optimizations in `before/` need no infrastructure. The CN steps in `after/` add infrastructure only when you need it.

## Run it

- [`before/README.md`](before/README.md) — run the sequential server, observe serialization, then follow the full pre-CN optimization path (ollama on Mac or vLLM on GPU)
- [`after/README.md`](after/README.md) — Setup: run the batching server, observe parallelism and metrics; Step 1: apply KEDA; Step 2: configure MIG

---

[← Back to Pain O.01](../../pains/O01-gpu-underutilized.md) · [Landscape](../../README.md) · [Examples index](../README.md)
