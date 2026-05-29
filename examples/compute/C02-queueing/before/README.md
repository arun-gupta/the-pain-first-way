# Before: the raw way

Submit Jobs directly. No queue, no priority, no visibility.

## What you'll observe

Three jobs are submitted. Two get pods immediately. The third is silently blocked.

`kubectl get jobs` shows all three as `Running` — misleading. `kubectl get pods` tells the truth: only two pods exist. `experiment-c` has no pod, no ETA, and no visible position. Finding out why requires digging through `kubectl describe` Events.

This is exactly what happens with GPUs on a shared cluster. Replace "1 CPU" with "1 A100" and the experience is identical.

Each job runs 20 epochs at 10 seconds each (~200 seconds total). `experiment-c` waits the full duration of two jobs before it can start. On a real GPU cluster each epoch might take 30-60 minutes, so the same wait is measured in hours, not minutes. The simulation compresses that to something you can observe in a single terminal session.

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

## 1. Create a Kind cluster

```bash
kind create cluster --name kind
```

## 2. Run it

First, apply the namespace quota and wait for it to be active. This simulates a shared cluster where your team's allocation is 2 GPU slots. On a well-resourced machine (M4, 32-core workstation) the jobs would otherwise all schedule immediately and the pain wouldn't land.

```bash
kubectl apply -f quota.yaml
kubectl describe resourcequota team-gpu-quota
```

You should see both limits set before continuing:

```
Resource         Used  Hard
--------         ----  ----
requests.cpu     0     2
requests.memory  0     512Mi
```

If `Hard` shows `0` or is blank, wait a moment and re-run the describe. Then apply the jobs:

> **Note:** the quota is a simulation device. In this demo it stands in for a real shared GPU cluster where someone else already holds most of the allocation. It is not something you'd add to fix the problem — that's what Kueue does in the `after/` folder.

Apply the three jobs at once:

```bash
kubectl apply -f jobs.yaml
```

Now check the jobs:

```bash
kubectl get jobs
```

```
NAME           STATUS    COMPLETIONS   DURATION   AGE
experiment-a   Running   0/1           9s         9s
experiment-b   Running   0/1           9s         9s
experiment-c   Running   0/1           9s         9s
```

All three say `Running`. But check the pods:

```bash
kubectl get pods
```

```
NAME                   READY   STATUS    RESTARTS   AGE
experiment-a-xxxxx     1/1     Running   0          25s
experiment-b-xxxxx     1/1     Running   0          25s
```

`experiment-c` has no pod. The jobs view lied. To find out why:

```bash
kubectl describe job experiment-c
```

The answer is buried in the Events section at the bottom:

```
Warning  FailedCreate  ... pods "experiment-c-xxxxx" is forbidden: exceeded quota: team-gpu-quota, requested: requests.cpu=1, used: requests.cpu=2, limited: requests.cpu=2
```

Or skip the noise and go straight to the events:

```bash
kubectl get events --field-selector involvedObject.name=experiment-c,reason=FailedCreate
```

```
LAST SEEN   TYPE      REASON        OBJECT          MESSAGE
2m          Warning   FailedCreate  job/experiment-c  pods "experiment-c-xxxxx" is forbidden: exceeded quota: team-gpu-quota, requested: requests.cpu=1, used: requests.cpu=2, limited: requests.cpu=2
```

Not obvious. Not actionable. That's the pain.

## The questions you can't answer

```bash
# Where is experiment-c?
kubectl get pods --field-selector=status.phase=Pending
# No resources found in default namespace.
# The pod doesn't exist. The job is blocked but there's nothing to observe.

# Why is it blocked?
kubectl get events --field-selector involvedObject.name=experiment-c,reason=FailedCreate
# FailedCreate with exceeded quota. No ETA. No position in a queue.

# Which team is using all the resources?
kubectl get pods -A --field-selector=status.phase=Running
# Tells you pods. Tells you nothing about quotas or allocations.

# Can I preempt a lower-priority job for my production workload?
# No mechanism to express priority at all.
```

## Clean up

```bash
kubectl delete -f jobs.yaml
kubectl delete -f quota.yaml
kind delete cluster --name kind
```

## What this costs in the real world

- A researcher submits a 20-hour training run and waits 6 hours in `Pending`.
- A production fine-tune that needs to ship by morning is stuck behind weekend experiments.
- No one knows whose job to cancel to unblock the queue.
- The cluster has idle capacity on a different node pool, but no one thought to check.

The cloud native answer: a queue with declared quotas, priorities, and fair sharing so every job has a visible position and an expected start time.

The [after/](../after/) folder shows how Kueue provides all of that.
