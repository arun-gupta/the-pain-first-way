# Before: the naive way

Two processes, no coordination. One starts late. The whole run dies.

## What you'll observe

You launch the master and worker in separate terminals. The master opens a
rendezvous socket and waits up to 10 seconds for the worker. The worker
simulates a slow start (image still pulling, node under memory pressure) by
sleeping 15 seconds before connecting.

The master times out and exits. The worker wakes up, tries to connect, and finds
nothing listening. Both processes fail. No training happens.

This is the distributed-training equivalent of an NCCL hang: one peer is
missing, so the whole collective blocks forever waiting.

## Prerequisites

- Python 3.8+

No Docker, no Kubernetes, no cluster required.

## Run it

Open **two terminals** in this directory.

**Terminal 1 — master (rank 0):**

```bash
RANK=0 WORLD_SIZE=2 RENDEZVOUS_TIMEOUT=10 python train.py
```

**Terminal 2 — worker (rank 1), started immediately:**

```bash
RANK=1 WORLD_SIZE=2 MASTER_ADDR=localhost WORKER_STARTUP_DELAY=15 python train.py
```

## Watch the failure

**Terminal 1** blocks waiting for the worker:

```
[rank 0] Starting. WORLD_SIZE=2 MASTER=localhost:29500
[rank 0] Opening rendezvous on :29500. Waiting up to 10s for 1 worker(s) ...
```

After 10 seconds the master gives up:

```
[rank 0] RENDEZVOUS TIMEOUT: only 0/1 worker(s) showed up within 10s.
[rank 0] This is what an NCCL hang looks like: the collective blocks forever
         waiting for a peer that never arrives.
```

**Terminal 2** sleeps 15 seconds, then tries to connect:

```
[rank 1] Starting. WORLD_SIZE=2 MASTER=localhost:29500
[rank 1] Simulating slow start: sleeping 15s (represents a node still pulling
         the image or under memory pressure).
[rank 1] Connecting to master at localhost:29500 (timeout: 60s) ...
[rank 1] RENDEZVOUS TIMEOUT: could not reach master at localhost:29500 within 60s.
         Aborting.
```

Both processes exit non-zero. No training happened.

## The questions you can't answer

- Which process failed first, and why?
- Was it a slow image pull, an OOM, or a scheduling delay?
- Can I restart just the worker and let the master pick up? No. The master
  already exited. Both must restart from scratch.
- On a real 32-GPU job at hour 6: all 6 hours of A100 time are gone. Start over.

## What this costs in the real world

Without gang scheduling, there is no guarantee all pods start at the same time.
Without a training operator, there is no fault-tolerant rendezvous. One slow
node kills the entire run.

The [after/](../after/) folder shows how the Training Operator provides that.
