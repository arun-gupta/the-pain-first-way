# Pain 4 example: topology-aware GPU placement with DRA

A working demonstration of [Pain 4: I asked for two GPUs and got two GPUs — but they can't talk to each other](../../pains/04-whole-gpus-only.md). Two scenarios, two manifest sets. The scheduler is the only thing that changes.

## What's here

```
04-whole-gpus-only/
├── before/                         # the raw way: integer GPU count, no topology
│   ├── kind-config.yaml            # 2-worker Kind cluster
│   ├── pod-topology.yaml           # nvidia.com/gpu: 2 — no interconnect constraint
│   ├── pod-affinity.yaml           # workaround: nodeAffinity on topology labels
│   ├── pod-mig.yaml                # nvidia.com/gpu: 1 — no MIG profile constraint
│   ├── allreduce.py                # bandwidth simulation (no GPU, no cluster needed)
│   └── README.md
└── after/                          # DRA: structured claims, scheduler-enforced topology
    ├── device-class.yaml           # DeviceClass: defines the GPU category (cluster admin)
    ├── resource-claim-topology.yaml # ResourceClaim: 2 GPUs, same NVLink domain
    ├── resource-claim-mig.yaml     # ResourceClaim: 3g.40gb MIG slice specifically
    ├── pod-topology.yaml           # Pod using the topology claim
    ├── pod-mig.yaml                # Pod using the MIG claim
    └── README.md
```

`before/` runs on a Kind cluster (CPU stands in for GPU slots). `after/` requires Kubernetes 1.34 with a vendor DRA driver — provided as reference YAML for real hardware.

## The point of the diff

`before/` submits pods that request GPU counts. The scheduler fills the count. It cannot check interconnect topology or MIG profile. Workloads land on the wrong hardware or fail at runtime when memory is insufficient.

`after/` uses `ResourceClaim` objects that describe what the workload actually needs: two GPUs sharing an NVLink domain, or a MIG slice with 40 GB HBM. The scheduler matches those claims against structured device advertisements (`ResourceSlice`) published by the DRA driver. No labels, no affinity rules, no manual per-node steps.

## Run it

- [`before/README.md`](before/README.md) — observe the pain (runnable in Kind + Python simulation)
- [`after/README.md`](after/README.md) — DRA reference YAML for real hardware

---

[← Back to Pain 4](../../pains/04-whole-gpus-only.md) · [Landscape](../../README.md) · [Examples index](../README.md)
