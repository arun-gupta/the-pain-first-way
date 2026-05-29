# Pain C.04 example: Multi-node training with PyTorchJob

A working demonstration of [Pain C.04: Multi-node training keeps falling over](../../pains/C04-multi-node-training.md). Same distributed training simulation, two submission styles. The Kubernetes manifests are the only thing that changes.

**Demonstrates:** PyTorchJob (Kubeflow Training Operator) · gang scheduling

## What's here

```
C04-multi-node/
├── before/        # the naive way: two bare Jobs racing to find each other
│   ├── train.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── build.sh              # build dist-training:latest here first
│   ├── dist-job.yaml         # Service + master Job + worker Job (no gang scheduling)
│   └── README.md
└── after/          # the cloud native way
    ├── train.py              # distributed training simulator (socket rendezvous)
    ├── Dockerfile
    ├── .dockerignore
    ├── build.sh
    ├── kind-config.yaml      # 3-node Kind cluster (1 control-plane + 2 workers)
    ├── pytorchjob.yaml       # PyTorchJob: 1 master + 1 worker, operator-coordinated
    └── README.md
```

No GPU required. Socket-based rendezvous stands in for NCCL; the scheduling and
failure mechanics are identical.

## The point of the diff

`before/dist-job.yaml` submits two separate Jobs. There is no gang scheduling: the
master opens a rendezvous server and waits, but the worker pod starts late (simulating
a node still pulling the image). The master times out. Both jobs fail. No training
happened.

`after/pytorchjob.yaml` submits a single `PyTorchJob`. The Training Operator creates
both pods together on separate Kind nodes (via `podAntiAffinity`), injects `MASTER_ADDR`,
`RANK`, and `WORLD_SIZE` automatically, and handles failure semantics at the
distributed-job level. Rendezvous succeeds. Training completes across two nodes.

## Run it

- [`before/README.md`](before/README.md) — observe the pain
- [`after/README.md`](after/README.md) — install the Training Operator, observe coordination in action

---

[← Back to Pain C.04](../../pains/C04-multi-node-training.md) · [Landscape](../../README.md) · [Examples index](../README.md)
