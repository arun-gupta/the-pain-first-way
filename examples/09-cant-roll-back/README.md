# Pain 9 example: zero-downtime rollout and rollback

A working demonstration of [Pain 9: I can't roll back a bad model without downtime](../../pains/09-cant-roll-back.md). Both scenarios use the same bad image update — the only difference is the rollout strategy and the presence of a readiness probe.

## What's here

```
09-cant-roll-back/
├── build.sh                     # builds model-server:v1 and model-server:v2-bad, loads both into Kind
├── before/                      # RollingUpdate, no readiness probe
│   ├── deployment-v1.yaml       # v1 Deployment using model-server:v1
│   ├── service.yaml             # stable Service for traffic checks
│   └── README.md
├── images/
│   ├── v1/Dockerfile            # good image: nginx serves normally
│   └── v2-bad/Dockerfile        # bad image: container starts, never serves HTTP
└── after/                       # RollingUpdate + readiness probe
    ├── deployment-v1.yaml       # v1 Deployment with readiness gate
    ├── service.yaml             # stable Service for traffic checks
    └── README.md
```

Both scenarios run on a local Kind cluster. No GPU required. The bad rollout is triggered the same way teams usually do it in practice: `kubectl set image deployment/model-server server=model-server:v2-bad`.

## Shared setup

Run these once from `examples/09-cant-roll-back/` before trying either scenario.

### Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [Docker](https://docs.docker.com/get-docker/)

### 1. Navigate to this directory

```bash
cd examples/09-cant-roll-back
```

### 2. Create a Kind cluster

If you already have a Kind cluster named `kind` from a previous example, you can skip this step.

```bash
kind create cluster --name kind 2>/dev/null || echo "Cluster already exists, reusing it."
```

### 3. Build and load the demo images

```bash
./build.sh
```

This builds `model-server:v1` and `model-server:v2-bad`, then loads both into your Kind cluster. No registry needed.

## The point of the diff

`before/` uses the default `RollingUpdate` strategy with no readiness probe. The Deployment reports success even though the new pods serve nothing, and the Service starts routing traffic to broken pods because Kubernetes has no health signal to stop it.

`after/` starts new pods before touching old ones (RollingUpdate). The readiness probe fails on v2-bad — the rolling update stalls, v1 keeps serving, and `kubectl rollout undo` reverts to the tracked previous revision in one command.

## Run it

- [`before/README.md`](before/README.md) — after completing shared setup, observe the false success report and broken traffic
- [`after/README.md`](after/README.md) — using the same cluster and demo images, observe the stalled rollout and clean rollback

---

[← Back to Pain 9](../../pains/09-cant-roll-back.md) · [Landscape](../../README.md) · [Examples index](../README.md)
