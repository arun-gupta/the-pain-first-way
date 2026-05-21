# Pain 7 example: the same traffic, three layers of improvement

A working demonstration of [Pain 7: My GPU sits at 30% but my bill says 100%](../../pains/07-gpu-underutilized.md). Same inference server, same simulated workload, three independent improvements applied one at a time. No GPU required.

## What's here

```
07-gpu-underutilized/
├── before/
│   ├── server.py          # naive sequential server — the problem
│   ├── vllm-commands.md   # pre-CN fixes: continuous batching, quantization, prefix caching, speculative decoding
│   └── README.md
└── after/                 # three incremental CN fixes
    ├── server.py          # Step 1: concurrent batching server with /metrics endpoint
    ├── deployment.yaml    # Step 1: Kubernetes deployment with Prometheus scrape annotations
    ├── scaledobject.yaml  # Step 2: KEDA scales on inference_requests_in_flight
    ├── mig-config.yaml    # Step 3: MIG profiles via GPU Operator (requires real GPU)
    └── README.md
```

No GPU required. All GPU behavior is simulated with `time.sleep`. The cloud-native concepts are identical to a real vLLM deployment.

## The point of the diff

`before/server.py` shows the problem: requests process one at a time, GPU idle between them. Five concurrent requests take ~2.5s wall time. CPU stays at 5% so Kubernetes HPA never triggers.

`before/vllm-commands.md` shows what ML practitioners do first — before touching infrastructure. Continuous batching, quantization, prefix caching, speculative decoding, sequence packing, and prefill/decode disaggregation are all vLLM launch flags. No Kubernetes required.

`after/server.py` simulates a batching-aware engine: up to `MAX_CONCURRENT` requests run in parallel, five concurrent requests take ~0.5s regardless of count, and `/metrics` exposes `inference_requests_in_flight` so the autoscaler watches the right signal.

`after/scaledobject.yaml` configures KEDA to add replicas when `inference_requests_in_flight` exceeds 3. `after/mig-config.yaml` shows how to partition a physical GPU into isolated slices via the GPU Operator so multiple workloads can share one card.

Each layer is independent. `vllm-commands.md` needs no infrastructure. Step 1 is a server swap. Steps 2 and 3 add infrastructure only when you need it.

## Run it

- [`before/README.md`](before/README.md) — run the sequential server, observe serialization, review vLLM pre-CN optimizations
- [`after/README.md`](after/README.md) — Step 1: run the batching server, observe parallelism and metrics; Step 2: apply KEDA; Step 3: configure MIG

---

[← Back to Pain 7](../../pains/07-gpu-underutilized.md) · [Landscape](../../README.md) · [Examples index](../README.md)
