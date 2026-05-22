# Before: integer GPU request with no topology awareness

Two scenarios — both caused by the same root problem: `nvidia.com/gpu: N` is a count, not a description. The scheduler can satisfy the count without knowing anything about the topology.

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- Python 3 (for the AllReduce simulation — no packages required)

## 0. Navigate to this directory

```bash
cd examples/04-whole-gpus-only/before
```

## 1. Create a Kind cluster

```bash
kind create cluster --name kind --config kind-config.yaml
```

## 2. Label nodes with fake GPU topology

On a real cluster, a DRA driver or a GPU operator publishes this information automatically. Without it, operators add labels by hand — which is exactly the problem:

```bash
kubectl label node kind-worker  topology.gpu/nvlink-domain=0 topology.gpu/switch=A nvidia.com/mig-profiles=3g.40gb
kubectl label node kind-worker2 topology.gpu/nvlink-domain=1 topology.gpu/switch=B nvidia.com/mig-profiles=1g.10gb
```

Verify:

```bash
kubectl get nodes -o custom-columns=\
'NAME:.metadata.name,DOMAIN:.metadata.labels.topology\.gpu/nvlink-domain,MIG:.metadata.labels.nvidia\.com/mig-profiles'
```

```
NAME           DOMAIN   MIG
kind-worker    0        3g.40gb
kind-worker2   1        1g.10gb
```

---

## Scenario 1: topology mismatch

### The raw request

Apply the pod with no topology constraints:

```bash
kubectl apply -f pod-topology.yaml
kubectl get pod two-gpu-no-topology -o wide
```

```
NAME                   READY   STATUS    NODE
two-gpu-no-topology    1/1     Running   kind-worker2
```

It landed on `kind-worker2`. That node has NVLink domain `1`. If the workload needs two GPUs in the same NVLink domain, it got the wrong node — or got the right node by luck. You have no guarantee either way.

Check the pod's output:

```bash
kubectl logs two-gpu-no-topology
```

```
scheduled on node: kind-worker2
no topology guarantee — could be any two GPUs
```

### The workaround — and why it breaks

Apply the pod that uses `nodeAffinity` to require `nvlink-domain=0`:

```bash
kubectl apply -f pod-affinity.yaml
kubectl get pod two-gpu-with-affinity -o wide
```

```
NAME                    READY   STATUS    NODE
two-gpu-with-affinity   1/1     Running   kind-worker
```

It landed on `kind-worker` — the node with domain `0`. The affinity rule worked.

Now add a third node without the topology label:

```bash
kind get kubeconfig --name kind > /tmp/kind.kubeconfig

# Kind doesn't support adding nodes dynamically.
# Simulate the effect by creating a pod that only the new node would accept
# by removing the label from one of the existing workers:
kubectl label node kind-worker2 topology.gpu/nvlink-domain-
```

Try to schedule another copy of the affinity pod:

```bash
kubectl run two-gpu-affinity-2 --image=busybox --restart=Never \
  --overrides='{"spec":{"affinity":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"topology.gpu/nvlink-domain","operator":"In","values":["0"]}]}]}}}},"containers":[{"name":"training","image":"busybox","command":["sh","-c","sleep 3600"],"resources":{"requests":{"cpu":"2"},"limits":{"cpu":"2"}}}]}}'
```

```bash
kubectl get pod two-gpu-affinity-2
```

```
NAME                 READY   STATUS    RESTARTS   AGE
two-gpu-affinity-2   0/1     Pending   0          30s
```

`Pending` — the pod cannot schedule because `kind-worker2` lost its label. No error says why. To find out:

```bash
kubectl describe pod two-gpu-affinity-2 | grep -A5 Events
```

```
Warning  FailedScheduling  ...  0/2 nodes are available: 1 node(s) didn't match
         Pod's node affinity/selector, 1 node(s) had untolerated taint.
```

This is the failure mode of hand-maintained labels: every new node is a new manual step. Miss it once and workloads silently queue.

Clean up the pending pod before the next step:

```bash
kubectl delete pod two-gpu-affinity-2 two-gpu-no-topology two-gpu-with-affinity
kubectl label node kind-worker2 topology.gpu/nvlink-domain=1  # restore the label
```

### Make the throughput penalty tangible

Run the AllReduce simulation locally — no cluster needed:

```bash
python3 allreduce.py
```

```
Ring AllReduce — 14 GB payload (7B model, FP16), 2 GPUs

  Scenario                                   Time        Notes
  ------------------------------------------ ----------  -----
  Same switch — NVIDIA NVLink 4.0              23.3 ms   baseline
  Same switch — AMD Infinity Fabric            35.0 ms   +50% slower
  Different switch — system RAM               280.0 ms   +1100% slower
```

The `different switch` row is what happens when `nvidia.com/gpu: 2` lands on a node where the two GPUs are on separate PCI switches. P2P transfers fall back to system RAM. For a single AllReduce over a 7B model, that's 280 ms instead of 23 ms — a cost paid on every gradient synchronisation step.

---

## Scenario 2: MIG profile mismatch

Nodes have different MIG profiles. `kind-worker` has `3g.40gb` slices (40 GB HBM each); `kind-worker2` has `1g.10gb` slices (10 GB HBM each). A large inference workload needs 40 GB. With the integer model it has no way to say so.

Apply the pod:

```bash
kubectl apply -f pod-mig.yaml
kubectl get pod large-inference -o wide
```

```
NAME              READY   STATUS    NODE
large-inference   1/1     Running   kind-worker2
```

It landed on `kind-worker2` — the node with `1g.10gb` slices. The scheduler saw `cpu: 1` available and placed it. It never read the `mig-profiles` label. On a real cluster this workload starts, loads the model, and runs out of GPU memory at runtime. The scheduling step gave no warning.

Check the node it landed on:

```bash
kubectl get node kind-worker2 --show-labels | tr ',' '\n' | grep mig
```

```
nvidia.com/mig-profiles=1g.10gb
```

The label was there. The scheduler just doesn't use it for pod placement — the integer model offers no vocabulary to match pods to profiles.

---

## Clean up

```bash
kubectl delete -f pod-topology.yaml -f pod-affinity.yaml -f pod-mig.yaml 2>/dev/null; true
kind delete cluster --name kind
```

## The questions you can't answer

```bash
# Are my two GPUs on the same NVLink domain?
kubectl get node kind-worker --show-labels
# You can read the labels — but the scheduler didn't use them.

# Why did my pod land on the wrong node?
kubectl describe pod large-inference
# No events mention MIG profiles. The scheduler considered the request satisfied.

# Can I request a specific MIG profile?
# No. nvidia.com/gpu: 1 is an integer. There is no nvidia.com/gpu-3g.40gb resource
# unless your cluster admin created a custom extended resource for each profile —
# which requires a separate device plugin and breaks when profiles change.
```

The [after/](../after/) folder shows how DRA replaces all three workarounds with first-class scheduler vocabulary.
