# Pain 8: Inference latency spiked and I can't tell why

> *Your model server's p99 jumped from 200ms to 4s overnight. Logs show nothing weird. You don't know if it's the model, the GPU, the network, the queue, or the upstream caller.*

## The pattern

You can't fix what you can't see. Production systems instrument three layers before traffic exists. Metrics over time, logs as discrete events, traces showing the path of one request across services.

## The primitives

- **Prometheus**: scrapes numeric metrics from your service (tokens/sec, queue depth, GPU utilization, p50/p95/p99)
- **OpenTelemetry**: instruments your code to emit traces and logs in a standard format
- **Grafana**: dashboards and alerts over the above

## Trade-offs

**What you keep**: your inference server code. vLLM, TGI, and FastAPI either expose Prometheus metrics already or are one decorator away.

**What you give up**: debugging from `print` statements after the fact. You instrument up front, or you stay blind.

---

[← Pain 7: Can't roll back](07-cant-roll-back.md) · [Landscape](../README.md) · [Pain 9: Costs out of control →](09-costs-out-of-control.md)
