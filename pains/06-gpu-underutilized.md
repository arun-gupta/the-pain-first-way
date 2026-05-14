# Pain 6: My GPU sits at 30% but my bill says 100%

> *Your inference server runs on an H100. `nvidia-smi` shows 30% utilization at p50 load. You're paying for the whole GPU every hour. Latency is fine, efficiency is awful.*

## The pattern

GPU utilization comes from feeding the GPU enough work per unit time. That's mostly a model-server config problem (batching, KV cache, sequence packing), but the layer around it matters too: routing enough requests to each replica, autoscaling on the right signal, sometimes sharing one GPU across multiple smaller workloads.

## The primitives

- **Continuous batching** (in vLLM, TGI, SGLang): not strictly cloud native, but the prerequisite for any of the rest to matter
- **Custom-metric HPA**: scale on tokens-per-second or queue depth, not CPU
- **Service mesh request routing**: hold a queue at the proxy so each replica stays busy without overloading
- **GPU sharing** (MIG, time-slicing): when one workload genuinely can't fill the card

## Trade-offs

**What you keep**: your model. The wins come from how you serve it.

**What you give up**: the comfort of "one GPU per workload" as a default. Efficiency comes from sharing and shaping.

---

[← Pain 5: Cold start](05-cold-start.md) · [Landscape](../README.md) · [Pain 7: Can't roll back →](07-cant-roll-back.md)
