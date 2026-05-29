# Pain C.03 example: topology-aware GPU placement with DRA

A working demonstration of [Pain C.03: I asked for two GPUs and got two GPUs — but they can't talk to each other](../../pains/C03-whole-gpus-only.md). Two scenarios, two manifest sets. The scheduler is the only thing that changes.

**Demonstrates:** Dynamic Resource Allocation (DeviceClass, ResourceClaim) · topology-aware scheduling

## What's here

```
C03-whole-gpus-only/
├── before/                          # integer GPU count: no topology awareness
│   ├── pod-topology.yaml            # nvidia.com/gpu: 2 — no interconnect constraint
│   ├── pod-mig.yaml                 # nvidia.com/gpu: 1 — no MIG profile constraint
│   └── README.md
└── after/                           # DRA: structured claims, scheduler-enforced topology
    ├── device-class.yaml            # DeviceClass: defines the GPU category (cluster admin)
    ├── resource-claim-topology.yaml # ResourceClaim: 2 GPUs, same NVLink domain
    ├── resource-claim-mig.yaml      # ResourceClaim: 3g.40gb MIG slice specifically
    ├── pod-topology.yaml            # Pod using the topology claim
    ├── pod-mig.yaml                 # Pod using the MIG claim
    └── README.md
```

Both `before/` and `after/` require real GPU nodes. `before/` runs on any cluster with NVIDIA GPU nodes and a device plugin. `after/` requires Kubernetes 1.34 with a vendor DRA driver.

## The point of the diff

`before/` submits pods that request GPU counts. The scheduler fills the count. It cannot check interconnect topology or MIG profile. Workloads land on the wrong hardware or fail at runtime when memory is insufficient.

`after/` uses `ResourceClaim` objects that describe what the workload actually needs: two GPUs sharing an NVLink domain, or a MIG slice with 40 GB HBM. The scheduler matches those claims against structured device advertisements (`ResourceSlice`) published by the DRA driver. No labels, no affinity rules, no manual per-node steps.

## Run it

Both scenarios require a real GPU cluster — this example has not been verified on live hardware yet.

- [`before/README.md`](before/README.md) — integer model: observe silent wrong placement (requires GPU nodes + NVIDIA device plugin)
- [`after/README.md`](after/README.md) — DRA reference YAML (requires Kubernetes 1.34 + vendor DRA driver + GPU nodes)

---

[← Back to Pain C.03](../../pains/C03-whole-gpus-only.md) · [Landscape](../../README.md) · [Examples index](../README.md)
