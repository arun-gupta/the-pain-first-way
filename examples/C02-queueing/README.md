# Pain C.02 example: GPU queueing with Kueue

A working demonstration of [Pain C.02: Can't get a GPU when I need one](../../pains/C02-cant-get-a-gpu.md). Same training job, two submission styles. The Kubernetes manifests are the only thing that changes.

## What's here

```
C02-queueing/
├── before/        # the typical way: raw Jobs competing for resources, no ordering
│   ├── jobs.yaml
│   └── README.md
└── after/         # the cloud native way
    ├── train.py              # the training workload (identical to C01-jobs/after)
    ├── Dockerfile
    ├── .dockerignore
    ├── build.sh
    ├── priority-classes.yaml # production (high) and experiment (low) PriorityClasses
    ├── resource-flavor.yaml  # ResourceFlavor: describes available hardware
    ├── cluster-queue.yaml    # ClusterQueue: quota and fair-sharing policy
    ├── local-queue.yaml      # LocalQueue: the per-team submission target
    ├── job-experiment.yaml   # three low-priority experiment jobs
    ├── job-production.yaml   # one high-priority production job
    └── README.md
```

No GPU required. CPU resources stand in for GPU slots; the scheduling mechanics are identical.

## The point of the diff

`before/jobs.yaml` submits three jobs directly. They compete for nodes with no ordering, no priority, and no answer to "when will mine run?"

`after/` installs Kueue, declares a quota, and attaches priority classes to jobs. The queue admits two jobs at a time. A third experiment job waits. When you submit a production job, it jumps the queue. You can see every workload's position and admission status with one command.

## Run it

- [`before/README.md`](before/README.md) -- observe the pain
- [`after/README.md`](after/README.md) -- install Kueue, observe the queue in action

---

[← Back to Pain C.02](../../pains/C02-cant-get-a-gpu.md) · [Landscape](../../README.md) · [Examples index](../README.md)
