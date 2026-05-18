# Before: the naive way

Submit two bare Jobs. No gang scheduling, no coordinated start, no recovery semantics.

## What you'll observe

Two Jobs are submitted at the same time. The master pod starts its rendezvous server
and waits 60 seconds for the worker to connect. The worker pod simulates a slow start
(a node still pulling the image, or under memory pressure) by sleeping 90 seconds
before attempting to connect.

The master times out at 60 seconds and exits with an error. Both Jobs end up in a
failed state. No training happens. This is the distributed-training equivalent of an
NCCL hang: one peer is missing, so the whole run dies.

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- A running Kind cluster (`kind create cluster` if you don't have one)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

## Build the image

```bash
./build.sh
```

This builds `dist-training:latest` and loads it into your Kind cluster. The
`after/` example uses the same image — no rebuild needed when you move there.

## Run it

Apply both resources in one command:

```bash
kubectl apply -f dist-job.yaml
```

This creates the ClusterIP Service, the master Job, and the worker Job simultaneously.

## Watch the failure

Open two terminals.

**Terminal 1 — master logs:**

```bash
kubectl logs -f job/dist-master
```

```
[rank 0] Starting. WORLD_SIZE=2 MASTER=dist-master:29500
[rank 0] Opening rendezvous on :29500. Waiting up to 60s for 1 worker(s) ...
```

The master is now blocked, waiting for a worker that hasn't connected yet.

**Terminal 2 — worker logs:**

```bash
kubectl logs -f job/dist-worker
```

```
[rank 1] Starting. WORLD_SIZE=2 MASTER=dist-master:29500
[rank 1] Simulating slow start: sleeping 90s (represents a node still pulling
         the image or under memory pressure).
```

At the 60-second mark, the master gives up:

```
[rank 0] RENDEZVOUS TIMEOUT: only 0/1 worker(s) showed up within 60s.
[rank 0] This is what an NCCL hang looks like: the collective blocks forever
         waiting for a peer that never arrives.
```

Check job status:

```bash
kubectl get jobs
```

```
NAME          STATUS   COMPLETIONS   DURATION   AGE
dist-master   Failed   0/1           61s        62s
dist-worker   Running  0/1                      62s
```

The worker eventually wakes up and tries to connect, but the master pod is already gone:

```
[rank 1] Connecting to master at dist-master:29500 (timeout: 60s) ...
[rank 1] RENDEZVOUS TIMEOUT: could not reach master at dist-master:29500 within 60s.
         Aborting.
```

Both jobs are now failed.

## The questions you can't answer

```bash
# Which pod failed first?
kubectl get pods
# You see both as Failed but nothing about the ordering or causal relationship.

# Was it a slow image pull, an OOM, or a scheduling delay?
kubectl describe job dist-worker
# Events mention pod creation but not why the worker was late.

# Can I just restart the worker and let the master pick up?
# No. The master exited. Both pods must restart together from scratch.

# How long will it take on a real GPU cluster?
# A 32-node job at hour 6: 6 hours of A100 time gone. Start over.
```

## Clean up

```bash
kubectl delete -f dist-job.yaml
```

## What this costs in the real world

- A 32-GPU job across 4 nodes: one node hiccups at hour 6. NCCL hangs. You wait
  for the timeout (often 30+ minutes). Then the whole run dies.
- Or: three workers start, the fourth is still pulling a 20 GB image. The others
  time out. You restart from scratch.
- Without gang scheduling, there is no guarantee all pods start at the same time.
  Without a training operator, there is no fault-tolerant rendezvous.

The cloud native answer: let the platform understand that this is a distributed job
and treat all N pods as a single unit — start together or not at all.

The [after/](../after/) folder shows how the Training Operator provides that.
