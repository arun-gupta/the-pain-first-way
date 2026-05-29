# before/ -- an in-memory agent loses the task when it restarts

The agent keeps its progress in process memory. Kill the pod mid-task and a
fresh one starts over from the top. Because the idempotency key was never
persisted, the retry invents a new one, the sink cannot dedupe it, and the
customer is charged twice.

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

No Docker or image build is needed: the agent and the sink run on the stock
`python:3.12-slim` image with their code mounted from a ConfigMap. The same
Kind cluster and sink are reused by the `after-*` variants, so set them up
once here.

> **If you ran the [G.03 example](../../../governance/G03-deploy-guardrails/) on this
> cluster**, its Kyverno admission policy is still enforcing and will block these
> workloads (a `docker.io` image, no governance labels). Remove it with
> `kubectl delete clusterpolicy deploy-guardrails`, or run this example on a fresh Kind
> cluster.

## Create a Kind cluster

If you already have a Kind cluster named `kind`, skip this.

```bash
kind create cluster --name kind 2>/dev/null || echo "Cluster already exists, reusing it."
```

## Deploy the sink

The sink is a small stand-in for the external systems the agent calls (a
payment API, an email service). It records each side effect and counts how many
charges it received, so the demo can show whether a crash caused a duplicate.
It also deduplicates by idempotency key, the way a real payment API does. Bring
it up once and leave it running: `before/` uses it now, and `after-postgres/`
reuses it (as will `after-queue/` and `after-argo/` once built), so every variant
charges the same external system. From this `before/` directory:

```bash
kubectl create configmap sink-code --from-file=../shared/sink/sink.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f ../shared/sink/sink.yaml
kubectl rollout status deploy/sink
```

## Deploy the agent

The whole walkthrough runs in **one terminal**, one command at a time. There is no
port-forward and no second window to manage. Mount the agent's code and start it:

```bash
kubectl create configmap agent-code \
  --from-file=main.py --from-file=../shared/agent_task.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f agent.yaml
```

## Step 1: let the task finish, confirm one charge

Follow the log until the task completes:

```bash
kubectl logs -f deploy/payments-agent
```

```
[agent] task user-task-1: resuming, already done = nothing
[agent]   reserve: side effect sent (key=user-task-1:reserve:9f3a...) -> sink: recorded
[agent]   reserve: recorded done
[agent]   charge: side effect sent (key=user-task-1:charge:1b7c...) -> sink: recorded
[agent]   charge: recorded done
[agent]   email: side effect sent (key=user-task-1:email:5d2e...) -> sink: recorded
[agent]   email: recorded done
[agent]   confirm: side effect sent (key=user-task-1:confirm:adc4...) -> sink: recorded
[agent]   confirm: recorded done
[agent] task user-task-1: complete
```

When you see `complete`, press Ctrl-C to stop following, then check the sink:

```bash
../shared/check-charges.sh
```

```
total effects: 4 | charges: 1
```

One charge. This is the baseline.

## Step 2: restart the agent, watch it charge again

Delete the pod. The Deployment recreates it as a brand-new process, which is what
happens when a node fails or the agent is redeployed mid-task:

```bash
kubectl delete pod -l app=payments-agent
```

Follow the new pod in the same terminal:

```bash
kubectl logs -f deploy/payments-agent
```

```
[agent] task user-task-1: resuming, already done = nothing
[agent]   reserve: side effect sent (key=user-task-1:reserve:c40d...) -> sink: recorded
...
[agent]   charge: side effect sent (key=user-task-1:charge:8e21...) -> sink: recorded
...
[agent] task user-task-1: complete
```

The fresh process started from `already done = nothing` and ran every step again,
sending `charge` with a *different* key. Ctrl-C, then check the sink once more:

```bash
../shared/check-charges.sh
```

```
total effects: ... | charges: 2
   charge user-task-1:charge:1b7c...
   charge user-task-1:charge:8e21...
```

## What to verify

| After | `check-charges.sh` shows | meaning |
|---|---|---|
| Step 1 | `charges: 1` | the task ran once |
| Step 2 | `charges: 2`, two different keys | the restart charged the customer a second time |

Two charges for one task. The in-memory agent recorded nothing outside the process, so
a fresh pod repeated the whole task, and because it never persisted the original
idempotency key, the retry could not reuse it. (With no durable state, deleting the pod
at *any* point after the `charge` line, mid-task or after completion, produces the
duplicate. Timing does not matter here; it will for `after-postgres/`.)

## Clean up before moving on

Leave the sink and cluster running for the `after-*` variants. Remove the
agent and reset the sink so the next run starts from a clean count:

```bash
kubectl delete -f agent.yaml
kubectl delete configmap agent-code
kubectl rollout restart deploy/sink
```

Then continue to [`../after-postgres/README.md`](../after-postgres/README.md),
where the same task survives the same crash.

---

[← Example overview](../README.md)
