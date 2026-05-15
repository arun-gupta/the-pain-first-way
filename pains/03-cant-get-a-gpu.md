# Pain 3: I can't get a GPU when I need one

> *You submit a training job. It sits `Pending` for hours. The cluster has GPUs but they're all claimed. You don't know who's using them, when they'll free up, or whether your job will ever schedule.*

## The pattern

GPUs are a constrained resource, and constrained resources benefit from a queue, a priority order, and a clear answer to "when will my job run?" In cloud native, the scheduler handles this; without it, the equivalent is team coordination.

## The primitives

- **Kueue**: native Kubernetes job queueing with quotas, priorities, and fair sharing per team
- **PriorityClasses**: production inference outranks experiments; high-priority jobs preempt lower ones if needed
- **GPU sharing** (MIG, time-slicing, MPS): one A100 or H100 split across multiple smaller workloads when you don't need a whole one
- **Cluster autoscaler with GPU node pools**: capacity comes online when the queue grows, scales down when idle

## Trade-offs

**What you keep**: your training and inference code.

**What you give up**: walking up to a box and grabbing it. Allocation becomes declared, queued, and visible.

---

[← Pain 2: GPU job crashed](02-gpu-job-crashed.md) · [Landscape](../README.md) · [Pain 4: Multi-node training →](04-multi-node-training.md)
