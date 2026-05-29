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

## Create a Kind cluster

If you already have a Kind cluster named `kind`, skip this.

```bash
kind create cluster --name kind 2>/dev/null || echo "Cluster already exists, reusing it."
```

## Deploy the sink

The sink is the external system the agent charges. Bring it up once; every
variant reuses it. From this `before/` directory:

```bash
kubectl create configmap sink-code --from-file=../shared/sink/sink.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f ../shared/sink/sink.yaml
kubectl rollout status deploy/sink
```

## Deploy the non-durable agent

Mount the agent's code (its `main.py` plus the shared task) and start it:

```bash
kubectl create configmap agent-code \
  --from-file=main.py --from-file=../shared/agent_task.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f agent.yaml
```

Watch it work through the steps:

```bash
kubectl logs -f deploy/payments-agent
```

```
[agent] task user-task-1: resuming, already done = nothing
[agent]   reserve: side effect sent (key=user-task-1:reserve:9f3a...) -> sink: recorded
[agent]   reserve: recorded done
[agent]   charge: side effect sent (key=user-task-1:charge:1b7c...) -> sink: recorded
```

## Crash it mid-task

While the log sits on the `charge` step (before `charge: recorded done`),
delete the pod in another terminal. The Deployment immediately recreates it:

```bash
kubectl delete pod -l app=payments-agent
```

Follow the new pod's logs:

```bash
kubectl logs -f deploy/payments-agent
```

```
[agent] task user-task-1: resuming, already done = nothing
[agent]   reserve: side effect sent (key=user-task-1:reserve:c40d...) -> sink: recorded
[agent]   charge: side effect sent (key=user-task-1:charge:8e21...) -> sink: recorded
```

It started over from `nothing`, and the `charge` key is different from the
first attempt.

## See the duplicate charge

```bash
../shared/check-charges.sh
```

```
total effects: ... | charges: 2
   charge user-task-1:charge:1b7c...
   charge user-task-1:charge:8e21...
```

Two charges for one task. Nothing recorded what the agent had already done, and
nothing let the retry reuse the original key.

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
