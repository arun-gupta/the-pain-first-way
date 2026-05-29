# after-postgres/ -- step state in Postgres survives the restart (option B)

The same agent, the same task, the same crash. The only change is the store:
step state now lives in a Postgres table instead of process memory, and the
idempotency key is derived from the durable task id. Kill the pod mid-task and
the new one reloads what is done, resumes, and the customer is charged once.

This is option B from the [overview](../README.md): you assemble all three
parts, and Postgres makes part 1 (state) and part 2 (idempotency) visible as
plain SQL.

## Prerequisites

Do the [`before/`](../before/README.md) walkthrough first. It creates the Kind
cluster and the sink, which this variant reuses. If you skipped it, create the
cluster and deploy the sink now (from this directory):

```bash
kind create cluster --name kind 2>/dev/null || echo "reusing cluster"
kubectl create configmap sink-code --from-file=../shared/sink/sink.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f ../shared/sink/sink.yaml
kubectl rollout status deploy/sink
```

Reset the sink so charges start from zero:

```bash
kubectl rollout restart deploy/sink && kubectl rollout status deploy/sink
```

## Deploy Postgres

```bash
kubectl apply -f postgres.yaml
kubectl rollout status deploy/postgres
```

## Deploy the durable agent

```bash
kubectl create configmap agent-code \
  --from-file=main.py --from-file=../shared/agent_task.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f agent.yaml
kubectl logs -f deploy/payments-agent
```

The container pip-installs the `pg8000` driver on start (a few seconds), then:

```
[agent] task user-task-1: resuming, already done = nothing
[agent]   reserve: side effect sent (key=user-task-1:reserve) -> sink: recorded
[agent]   reserve: recorded done
[agent]   charge: side effect sent (key=user-task-1:charge) -> sink: recorded
```

Note the key has no random suffix: it is stable, derived from the task id.

## Crash it mid-task

While the log sits on the `charge` step, delete the pod:

```bash
kubectl delete pod -l app=payments-agent
kubectl logs -f deploy/payments-agent
```

This time the new pod reloads its progress from Postgres and resumes:

```
[agent] task user-task-1: resuming, already done = ['reserve']
[agent]   reserve: skip (already done)
[agent]   charge: side effect sent (key=user-task-1:charge) -> sink: duplicate-ignored
[agent]   charge: recorded done
[agent]   email: side effect sent (key=user-task-1:email) -> sink: recorded
[agent]   confirm: side effect sent (key=user-task-1:confirm) -> sink: recorded
[agent] task user-task-1: complete
```

It skipped `reserve`, and even though it re-sent `charge` (the crash landed
before that step was recorded done), the stable key let the sink dedupe it:
`duplicate-ignored`. If the crash had landed after `charge: recorded done`, the
resume would have skipped `charge` outright. Either path charges once.

## See the single charge

```bash
../shared/check-charges.sh
```

```
total effects: 4 | charges: 1
   charge user-task-1:charge
   ...
```

One charge. Inspect the durable state directly:

```bash
kubectl exec deploy/postgres -- psql -U postgres -d agent \
  -c "SELECT task_id, step FROM done_steps ORDER BY step;"
```

```
   task_id    |  step
--------------+---------
 user-task-1  | charge
 user-task-1  | confirm
 user-task-1  | email
 user-task-1  | reserve
```

That table is part 1 (state outside the process). The `ON CONFLICT` on its
primary key is part 2 (recording is idempotent too). `load_done` reading it on
startup is part 3 (resume from the last completed step).

## Re-run cleanly

The agent resumes a task by its id, so a second run finds every step already
done and charges nothing. To run the demo again from scratch, reset both
stores:

```bash
kubectl delete -f postgres.yaml && kubectl apply -f postgres.yaml
kubectl rollout restart deploy/sink
```

## Clean up

```bash
kubectl delete -f agent.yaml -f postgres.yaml
kubectl delete configmap agent-code
```

The sink and cluster stay up for the other variants (`after-queue/`,
`after-argo/`), which run the identical crash test with a different part 3.

---

[← Example overview](../README.md) · [before/](../before/README.md)
