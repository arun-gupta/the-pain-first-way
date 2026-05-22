# Pain 11: Costs are out of control

> *Your AI app's GPU bill tripled. Half your replicas are idle at 3am, the other half OOM'd at peak yesterday, and nobody capped how many GPUs the new fine-tuning experiment can grab.*

## The pattern

In cloud native, capacity follows demand. Workloads scale based on signal. Idle workloads scale down (within the warm-pool floor you set for cold start). Best-effort jobs ride cheap, preemptible capacity.

## The primitives

- **HPA (Horizontal Pod Autoscaler)**: replicas track a metric (CPU, GPU, custom)
- **KEDA**: HPA on event sources like queue length, Kafka lag, or a Prometheus query
- **Spot and preemptible nodes**: cheap capacity for training, fine-tuning, and other interruptible work
- **ResourceQuotas**: hard caps per team or namespace so one experiment can't eat the cluster

## Trade-offs

**What you keep**: your model server and your training jobs. The scaling and capping happen around them.

**What you give up**: the comfort of a fixed fleet. Capacity becomes elastic, and you have to think about what's interruptible.

---

[← Pain 10: Latency spiked](10-latency-spiked.md) · [Landscape](../README.md) · [Pain 12: Prompt version in prod →](12-prompt-version.md)
