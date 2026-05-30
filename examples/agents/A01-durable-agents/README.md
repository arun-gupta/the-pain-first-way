# Pain A.01 example: my agent died halfway through a user task

A working demonstration of [Pain A.01: My agent died halfway through a user
task](../../../pains/agents/A01-durable-agents.md). An agent runs a multi-step task
with real side effects (reserve, charge, email, confirm). `before/` holds the plan in
process memory, so killing the pod mid-task loses state and a retry duplicates the
side effects. `after/` makes the run durable, so killing the pod mid-task resumes from
the last completed step with no duplicate.

> **Status: option B available; C built, D next.** `before/` and `after-postgres/`
> (option B) are built and verified on a live Kind cluster, so the example is listed as
> Available in the catalog. `after-queue/` (option C) is built and pending a live
> shakedown; `after-argo/` (option D) is next.

## The three swappable parts

Durability is not one tool. As the pain describes, it is three parts you can assemble
independently:

1. **A state store** so a fresh process can read what the dead one had done.
2. **Idempotent side effects** so resuming cannot duplicate a charge or an email.
3. **A resume point** that reads the state and continues from the last completed step.

The options below all provide the same three parts. They differ in what you build by
hand versus what an engine supplies, and in how finely they resume.

## The five options at a glance

| Option | State store (part 1) | Idempotency (part 2) | Resume (part 3) | Resume granularity |
|---|---|---|---|---|
| **A** PVC + hand-rolled loop | PVC file | hand-coded key check | your checkpoint-and-resume loop | wherever you checkpoint |
| **B** Postgres + checkpointer | Postgres table | `INSERT ... ON CONFLICT` (visible) | your loop / saver reads last committed step | per committed step |
| **C** durable queue + worker | the queue message *is* the state | hand-coded key check | queue redelivers the unacked message | whole work item (coarsest) |
| **D** Argo Workflows | K8s API status + artifact repo | your keys; engine re-runs whole step | Argo skips finished DAG steps on retry | per step |
| **E** Temporal | Temporal's event history datastore | wanted; replay shrinks the window | Temporal replays history to rebuild state | per instruction (finest) |

A, B, and C are "you assemble all three parts." D and E are "the engine owns part 3
and brings its own part 1." Part 2 effort scales inversely with resume granularity:
the coarser the resume, the harder idempotency has to work. Each option is detailed
below with its own diagram.

## The options

### Option A: PVC + hand-rolled loop

Your loop checkpoints step state to a PersistentVolumeClaim and resumes from it on
restart. Zero extra infrastructure; the whole mechanism is readable in one file.

```mermaid
flowchart LR
  LOOP[your agent loop] --> STEP["step + side effect<br/>(idempotency key)"]
  STEP --> PVC[(PVC checkpoint file)]
  PVC --> LOOP
  RESTART((pod restart)) -.-> PVC
  PVC -.resume from last checkpoint.-> LOOP
```

### Option B: Postgres + checkpointer

State lives in a Postgres table; idempotency becomes a visible unique constraint
(`INSERT ... ON CONFLICT DO NOTHING`) instead of a hand-coded check. This is how most
real durable agents persist, and the closest honest fit to LangGraph-style savers.

```mermaid
flowchart LR
  LOOP[your agent loop] --> STEP["step + side effect<br/>(INSERT ON CONFLICT key)"]
  STEP --> PG[(Postgres step table)]
  PG --> LOOP
  RESTART((pod restart)) -.-> PG
  PG -.resume from last committed row.-> LOOP
```

### Option C: durable queue + worker

The queue holds the work item (part 1) and redelivers it if the worker dies before
acking (part 3). You still supply idempotency (part 2). Coarsest resume: the whole
work item is reprocessed. The queue itself is swappable; several cloud native backends
give the same ack-or-redeliver guarantee:

- **NATS JetStream** (CNCF): durable streams with explicit ack and redelivery.
- **Apache Kafka via Strimzi** (Strimzi is a CNCF project): durable log, consumer offsets.
- **RabbitMQ** (cluster operator): ack and requeue on the channel.
- **Apache Pulsar**: durable topics with negative-ack and redelivery.
- **Redis Streams**: consumer groups with `XACK` / `XCLAIM` for redelivery.

KEDA (CNCF) pairs with any of them to scale the worker pool on queue depth.

```mermaid
flowchart LR
  subgraph QUEUE ["durable queue: pick a CN backend"]
    direction TB
    NATS[NATS JetStream]
    KAFKA[Kafka via Strimzi]
    RMQ[RabbitMQ]
    PULSAR[Pulsar]
    REDIS[Redis Streams]
  end
  QUEUE --> W[worker pulls message]
  W --> STEP["step + side effect<br/>(idempotency key)"]
  STEP --> ACK[ack on success]
  ACK --> QUEUE
  RST((worker dies, no ack)) -.-> QUEUE
  QUEUE -.redeliver to new worker.-> W
```

### Option D: Argo Workflows

The engine owns part 3: Argo records which DAG steps finished (in the `Workflow` CRD
status, large outputs offloaded to an artifact repo) and skips them on retry. It
re-runs the *whole* failed step, so idempotency carries more weight.

```mermaid
flowchart LR
  ARGO[Argo controller] --> S1[step 1]
  S1 --> S2[step 2]
  S2 --> S3[step 3]
  S1 --> ST[(K8s API status<br/>+ artifacts)]
  S2 --> ST
  ST --> ARGO
  RESTART((step pod dies)) -.-> ARGO
  ARGO -.skip finished steps, re-run failed.-> S2
```

### Option E: Temporal

The engine owns part 3 at the finest granularity: Temporal replays an event history
to rebuild in-process state, so a restart resumes close to the instruction it died on.
Idempotency is still wanted, but the window for duplication is smallest.

```mermaid
flowchart LR
  TW[Temporal worker] --> ACT["activity + side effect<br/>(idempotency key)"]
  ACT --> EH[(event history)]
  EH --> TW
  RESTART((worker dies)) -.-> EH
  EH -.replay history, rebuild state.-> TW
```

## What this example implements

Three of the five options get a runnable `after-*` variant. All share the same
`before/` and the same [`shared/`](shared/) harness, so the crash test is identical and
only the durability mechanism differs:

- **B -- Postgres + checkpointer** ([`after-postgres/`](after-postgres/README.md),
  built): the honest core, where state (part 1) and idempotency (part 2) are visible as
  plain SQL on a plain Kind cluster.
- **C -- durable queue + worker** ([`after-queue/`](after-queue/README.md), built):
  NATS JetStream holds the work item and redelivers it on crash; with no per-step
  checkpoint the worker reprocesses the whole task, and the idempotency key prevents the
  duplicate.
- **D -- Argo Workflows** (`after-argo/`, next): the engine owns part 3, resuming at
  step granularity.

Build order is B then C then D, each verified on a live cluster before the next.

A and E stay as reference points in the matrix above rather than runnable variants: A
(hand-rolled PVC loop) is the same shape as B with a file in place of the database, and
E (Temporal) is a heavier engine whose instruction-level replay is hard to show
honestly without a full Temporal deployment.

## Run it

Run the variants in order; `before/` sets up the Kind cluster and the sink that the
rest reuse.

1. [`before/`](before/README.md) -- watch the in-memory agent charge twice after a crash.
2. [`after-postgres/`](after-postgres/README.md) -- the same crash, resumed from Postgres,
   charged once.
3. [`after-queue/`](after-queue/README.md) -- the same crash, redelivered by NATS
   JetStream and reprocessed whole, still charged once.

`after-argo/` (D) follows the same shape once built.

---

[← Back to Pain A.01](../../../pains/agents/A01-durable-agents.md) · [Landscape](../../../README.md) · [Examples index](../../README.md)
