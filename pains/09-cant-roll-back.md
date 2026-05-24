# Pain 9: I can't roll back a bad model without downtime

> *You pushed v3 of your model with `kubectl set image`. The rollout completed. p99 doubled and accuracy on your top intent dropped 4 points. You dig through CI logs trying to find the previous image tag. You didn't know `kubectl rollout undo` existed.*

## The pattern

Before Kubernetes, this was SSH, `scp` new weights, restart the process, and hope nothing is half-deployed. On Kubernetes the mechanism exists — Deployments, rollout history, `kubectl rollout undo` — but without a readiness probe, the platform has no signal to distinguish a healthy rollout from a broken one. The rollout completes. Traffic shifts. The bad model serves.

With a readiness probe, the platform gets that signal. A pod that fails its health check is never added to Service endpoints and never counted as a successful rollout step. A bad push stalls rather than completes, old pods keep serving, and rollback is a single command against tracked history.

Without a readiness probe, `RollingUpdate` replaces old pods with new ones regardless of whether they serve traffic:

```mermaid
graph LR
    V1["v1 pods serving"] -->|"kubectl set image\nno readiness probe"| R["rolling update\ncompletes"]
    R --> B["v2-bad pods\nget traffic"]
    B --> D["bad responses\nno automatic detection"]
```

With a readiness probe, the bad version never becomes live:

```mermaid
graph LR
    V1["v1 pods serving"] -->|"kubectl set image\nreadiness probe set"| P["new v2-bad pod starts\nprobe fails"]
    P --> S["rolling update stalls\nv1 keeps serving"]
    S -->|"kubectl rollout undo"| R["v1 restored\nzero downtime"]
```

## The primitives

**[Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)**: declares the desired state — N replicas of this image with these resources. The controller converges reality to match. Rollout history is tracked automatically.

**[Rolling update strategy](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment)**: replaces pods in batches. `maxUnavailable: 0` means no old pod is removed until a new one is ready. `maxSurge: 1` allows one extra pod during the transition.

**[Readiness probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)**: a health check the kubelet runs before marking a pod Ready. A pod that fails its readiness probe is never added to Service endpoints and is never counted as a successful rollout step. This is the gate that prevents a bad push from becoming live.

**`kubectl rollout undo`**: reverts the Deployment to the previous revision in its history. No manifest required — the controller applies the tracked previous spec.

**[Argo Rollouts](https://argoproj.github.io/rollouts/) / [Flagger](https://flagger.app/)**: extend the rollout primitive with canary and blue-green strategies. Route 5% of traffic to v3, watch p99, ramp or revert automatically based on metrics.

## Trade-offs

**What you keep**: your model server. The Deployment is a YAML manifest wrapping it.

**What you give up**: deploying as a verb you do. Deployment becomes a state you declare, and the platform converges to it. Health checks must reflect actual readiness — a probe that always passes gives no protection.

## Try it

A working demonstration lives in [`examples/09-cant-roll-back/`](../examples/09-cant-roll-back/). [`before/`](../examples/09-cant-roll-back/before/README.md) uses a `RollingUpdate` Deployment with no readiness probe — observe the rollout complete successfully while the new pods serve nothing, with no warning from Kubernetes. [`after/`](../examples/09-cant-roll-back/after/README.md) adds a readiness probe — the bad push stalls, v1 keeps serving, and `kubectl rollout undo` restores the previous version in one command. Both run on a local Kind cluster with no GPU required.

---

[← Pain 8: GPU underutilization](08-gpu-underutilized.md) · [Landscape](../README.md) · [Pain 10: Latency spiked →](10-latency-spiked.md)
