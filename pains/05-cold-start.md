# Pain 5: Cold start for my 70B model takes 4 minutes

> *A new replica needs to scale up. It pulls a 30GB image, downloads model weights from object storage, loads them into GPU memory, and warms the inference engine. Your users wait 4 minutes for the first response after a scale event.*

```mermaid
flowchart LR
    A[Pod scheduled] --> B[Pull 30GB image<br/>~90s]
    B --> C[Load weights to disk<br/>~120s]
    C --> D[Load to GPU memory<br/>~20s]
    D --> E[Engine warmup<br/>~10s]
    E --> F[Ready<br/>~4 min total]
```

## The pattern

Cold start is real cost in AI workloads, and the answer isn't "make the model smaller." It's keeping ready capacity, splitting what loads when, and caching aggressively at every layer.

## The primitives

- **Pre-pulled images on nodes**: cache the image so node startup doesn't repull 30GB
- **Init containers**: load weights into a shared volume before the main container starts
- **PVCs and node-local caches**: model weights stored once per node, mounted into pods
- **Warm pools and minimum replicas**: HPA's `minReplicas` higher than zero, plus headroom for traffic spikes
- **KServe and serving-aware autoscalers** (KEDA HTTP, Knative): frameworks that explicitly model load-once, serve-many

## Trade-offs

**What you keep**: your model and your model server.

**What you give up**: scale-to-zero as a default. For big models, the math usually favors a warm floor.

---

[← Pain 4: Multi-node training](04-multi-node-training.md) · [Landscape](../README.md) · [Pain 6: GPU underutilization →](06-gpu-underutilized.md)
