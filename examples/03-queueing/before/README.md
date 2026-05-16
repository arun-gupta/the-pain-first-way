# Before: the raw way

Submit Jobs directly. No queue, no priority, no visibility.

## What you'll observe

Three jobs compete for two available CPU slots. One sits `Pending`. You don't know:

- Which experiment will start next
- When the pending job will run
- Whether a critical production job could ever jump ahead
- Who else is consuming cluster resources and why

This is exactly what happens with GPUs on a shared cluster. Replace "1 CPU" with "1 A100" and the experience is identical.

Each job runs 20 epochs at 10 seconds each (~200 seconds total). `experiment-c` waits the full duration of two jobs before it can start. On a real GPU cluster each epoch might take 30-60 minutes, so the same wait is measured in hours, not minutes. The simulation compresses that to something you can observe in a single terminal session.

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- A running Kind cluster (`kind create cluster` if you don't have one)

## Run it

First, apply the namespace quota. This simulates a shared cluster where your team's allocation is 2 GPU slots. On a well-resourced machine (M4, 32-core workstation) the jobs would otherwise all schedule immediately and the pain wouldn't land.

```bash
kubectl apply -f quota.yaml
```

> **Note:** the quota is a simulation device. In this demo it stands in for a real shared GPU cluster where someone else already holds most of the allocation. It is not something you'd add to fix the problem — that's what Kueue does in the `after/` folder.

Apply the three jobs at once:

```bash
kubectl apply -f jobs.yaml
```

Watch what happens:

```bash
kubectl get pods -w
```

You'll see two pods reach `Running`. `experiment-c` never appears:

```
experiment-a-xxxxx   1/1   Running   0          3s
experiment-b-xxxxx   1/1   Running   0          3s
```

`experiment-c`'s pod was never created — the quota rejected it before Kubernetes could schedule anything. You won't see it in `get pods` at all.

To find it:

```bash
kubectl get jobs
```

```
NAME           COMPLETIONS   DURATION   AGE
experiment-a   0/1           10s        10s
experiment-b   0/1           10s        10s
experiment-c   0/1                      10s
```

`experiment-c` has no duration — it has never run. To find out why:

```bash
kubectl describe job experiment-c
```

The answer is buried in the Events section at the bottom:

```
Warning  FailedCreate  ... pods "experiment-c-xxxxx" is forbidden: exceeded quota: team-gpu-quota
```

Not obvious. Not actionable. That's the pain.

## The questions you can't answer

```bash
# Where is experiment-c?
kubectl get pods --field-selector=status.phase=Pending
# No resources found in default namespace.
# The pod doesn't exist. The job is blocked but there's nothing to observe.

# Why is it blocked?
kubectl describe job experiment-c
# FailedCreate buried in Events. No ETA. No position in a queue.

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
```

## What this costs in the real world

- A researcher submits a 20-hour training run and waits 6 hours in `Pending`.
- A production fine-tune that needs to ship by morning is stuck behind weekend experiments.
- No one knows whose job to cancel to unblock the queue.
- The cluster has idle capacity on a different node pool, but no one thought to check.

The cloud native answer: a queue with declared quotas, priorities, and fair sharing so every job has a visible position and an expected start time.

The [after/](../after/) folder shows how Kueue provides all of that.
