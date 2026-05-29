# shared/ -- the harness every variant reuses

The `before/` walkthrough and each `after-*` variant run the *same* agent task
against the *same* side-effect sink, so the only thing that changes between
them is how durability is provided. That shared machinery lives here.

## What's here

```
agent_task.py     # the task: reserve -> charge -> email -> confirm
sink/
  sink.py         # an idempotent side-effect recorder (stdlib only)
  sink.yaml       # Deployment + Service for the sink
check-charges.sh  # print the sink's recorded effects and the charge count
```

## The task

`agent_task.run(store)` walks four steps, each with a side effect sent to the
sink. It is mechanism-agnostic: durability comes entirely from the `store`
object a variant passes in, which answers three questions, one per durability
part:

| store method | durability part |
|---|---|
| `load_done(task_id)` | part 3, where to resume |
| `mark_done(task_id, step)` | part 1, state kept outside the process |
| `idempotency_key(task_id, step)` | part 2, side effects safe to retry |

`before/` passes an in-memory store (loses everything on restart, random
keys). Each `after-*` passes a durable one.

## The sink

`sink.py` stands in for the external systems an agent touches (a payment API,
an email service). `POST /effect` records an effect unless its idempotency key
was already seen; `GET /effects` reports the totals. This is what makes
exactly-once *visible*: after a correct resume `charges == 1`, and after a
crash that duplicated work `charges == 2`. State is in memory, so restart the
sink deployment (`kubectl rollout restart deploy/sink`) to reset between runs.

## The crash window

Each step sleeps (`STEP_DELAY`, default 5s) between sending its side effect
and recording it as done. Deleting the agent pod during that sleep is the
crash. A Deployment recreates the pod, which is the process restart that
`before/` cannot survive and the `after-*` variants can.

---

[← Example overview](../README.md)
