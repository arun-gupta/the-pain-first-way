# Before: integer GPU request with no topology awareness

**Prerequisites**: a Kubernetes cluster with NVIDIA GPU nodes and the NVIDIA device plugin installed.

`nvidia.com/gpu: N` is a count, not a description. The scheduler fills the count. It cannot check interconnect topology or MIG profile.

## Scenario 1: topology mismatch

```bash
kubectl apply -f pod-topology.yaml
kubectl logs two-gpu-no-topology
```

The pod gets two GPUs. If they are on different PCI switches, `nvidia-smi topo -m` shows `SYS` (traverses system RAM) instead of `NV4` (NVLink). peer-to-peer transfers fall back to system RAM — ~40% throughput penalty. No scheduling error; the scheduler considered the request satisfied.

## Scenario 2: MIG profile mismatch

```bash
kubectl apply -f pod-mig.yaml
kubectl logs large-inference
```

The pod gets one GPU. If the node has `1g.10gb` MIG slices rather than `3g.40gb`, `nvidia-smi` shows ~10 GB HBM instead of ~40 GB. The workload starts, loads the model, and OOMs at runtime. No scheduling error.

## Clean up

```bash
kubectl delete -f pod-topology.yaml -f pod-mig.yaml
```

---

The [after/](../after/) folder shows how DRA replaces the integer count with structured claims the scheduler can match against real device topology.
