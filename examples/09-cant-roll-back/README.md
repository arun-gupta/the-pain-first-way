# Pain 9 example: zero-downtime rollout and rollback

A working demonstration of [Pain 9: I can't roll back a bad model without downtime](../../pains/09-cant-roll-back.md). Both scenarios use the same bad image update — the only difference is the rollout strategy and the presence of a readiness probe.

## What's here

```
09-cant-roll-back/
├── before/                      # RollingUpdate, no readiness probe
│   ├── deployment-v1.yaml       # v1: nginx serving normally
│   ├── deployment-v2-bad.yaml   # v2: starts but never serves HTTP
│   ├── service.yaml             # stable Service for traffic checks
│   └── README.md
└── after/                       # RollingUpdate + readiness probe
    ├── deployment-v1.yaml       # v1: nginx with readiness gate
    ├── deployment-v2-bad.yaml   # v2: same bad update — now caught by the probe
    ├── service.yaml             # stable Service for traffic checks
    └── README.md
```

Both scenarios run on a local Kind cluster. No GPU required.

## The point of the diff

`before/` uses the default `RollingUpdate` strategy with no readiness probe. The Deployment reports success even though the new pods serve nothing, and the Service starts routing traffic to broken pods because Kubernetes has no health signal to stop it.

`after/` starts new pods before touching old ones (RollingUpdate). The readiness probe fails on v2-bad — the rolling update stalls, v1 keeps serving, and `kubectl rollout undo` reverts to the tracked previous revision in one command.

## Run it

- [`before/README.md`](before/README.md) — observe the downtime and false success report
- [`after/README.md`](after/README.md) — observe the stall, confirmed service continuity, and clean rollback

---

[← Back to Pain 9](../../pains/09-cant-roll-back.md) · [Landscape](../../README.md) · [Examples index](../README.md)
