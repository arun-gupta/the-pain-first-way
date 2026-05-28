# Pain C.01 example: the same training job, two fates

A working demonstration of [Pain C.01: GPU job crashed at hour 14](../../pains/C01-gpu-job-crashed.md). Same Python training code, two deployment styles. The Kubernetes manifests are the only thing that changes. And that changes everything.

## What's here

```
02-jobs/
├── before/        # the typical way: python train.py, no safety net
│   ├── train.py
│   └── README.md
└── after/         # the cloud native way
    ├── train.py         # IDENTICAL to before/train.py except for checkpoint logic
    ├── Dockerfile
    ├── .dockerignore
    ├── build.sh
    ├── pvc.yaml         # PersistentVolumeClaim: checkpoints survive pod death
    ├── job.yaml         # Kubernetes Job: platform retries, volume mounted
    └── README.md
```

No GPU required. The training loop is simulated (fake loss curve, 3 seconds per epoch). The cloud native concepts are identical to a real GPU job.

## The point of the diff

`before/train.py` has no checkpointing. Kill it at any epoch and it restarts from epoch 0.

`after/train.py` writes `checkpoint.json` after every epoch. On restart it reads the file and resumes from the next epoch. The Job manifest tells Kubernetes to retry on failure. The PVC keeps the checkpoint file alive between pod deaths.

Kill the pod at epoch 12. The replacement pod starts at epoch 13.

## Run it

- [`before/README.md`](before/README.md) -- run bare with Python, simulate a crash, observe the loss
- [`after/README.md`](after/README.md) -- build, apply, crash, watch the resume

---

[← Back to Pain C.01](../../pains/C01-gpu-job-crashed.md) · [Landscape](../../README.md) · [Examples index](../README.md)
