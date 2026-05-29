# Pain C.04: Multi-node training keeps falling over

> *Your distributed training job needs 32 GPUs across 4 nodes. One node hiccups at hour 6, NCCL hangs, the whole run dies. Or three workers come up, the fourth is still pulling the image, and the others time out waiting.*

## The pattern

Distributed training is all-or-nothing. The platform either gives you every node you asked for at the same time, with the right network and the ability to recover, or it doesn't start the job at all.

**Without gang scheduling — the failure mode:**

Without coordination, Kubernetes schedules pods as resources become available. One slow worker — still pulling the image, waiting for a GPU slot, or under memory pressure — means the master times out at the rendezvous barrier and the entire run dies. Every rank restarts from epoch 0.

```mermaid
sequenceDiagram
    participant K as Kubernetes
    participant M as Master pod (rank 0)
    participant W3 as Workers rank 1–3
    participant W4 as Worker rank 4<br/>(slow image pull)

    K->>M: Schedule pod ✓
    K->>W3: Schedule pods ✓
    K-->>W4: Still pulling image…

    M->>W3: Rendezvous: waiting for all 4 peers
    W3->>M: Connected ✓
    Note over M,W4: 30+ min timeout

    W4--xM: Never connects in time
    Note over M: NCCL hang → timeout → crash
    Note over M,W4: Entire run fails. Start over from epoch 0.
```

**With a training operator — the fix:**

The operator gang-schedules the job: all N pods are created together or none start. It injects `MASTER_ADDR`, `RANK`, and `WORLD_SIZE` automatically so the rendezvous always succeeds. When a single worker crashes, only that pod is replaced — the master keeps running and training continues.

```mermaid
sequenceDiagram
    participant OP as Training Operator
    participant M as Master pod (rank 0)
    participant W as Worker pods (rank 1–N)

    Note over OP: Gang-schedule: wait until<br/>all N pods can start together
    OP->>M: Create pod (injects MASTER_ADDR, RANK=0)
    OP->>W: Create pods (injects MASTER_ADDR, RANK=1…N)

    M->>W: Rendezvous ✓ (all peers present)
    Note over M,W: Training runs

    W--xW: One worker crashes (node failure)
    OP->>W: Restart failed pod only
    W->>M: Rejoin rendezvous ✓
    Note over M,W: Training continues
```

## The primitives

- **Gang scheduling** (Volcano, Kueue): the job starts when all N pods can run together, not pod-by-pod. The scheduler holds every pod in a pending state until the full set can be admitted simultaneously. If the cluster doesn't have room for all N pods right now, none start. This eliminates the partial-start race where some ranks are running while others are still waiting to be scheduled.
- **Training operators** (KubeRay, PyTorchJob, MPIJob, TorchX): primitives that understand distributed training semantics, including elastic recovery. PyTorchJob is demonstrated in the example; KubeRay serves Ray-based workloads, MPIJob covers MPI-based training (Horovod), and TorchX is a launcher abstraction that can target any of them.
- **High-performance networking**: RDMA, GPUDirect, configured at the node and CNI layer so NCCL isn't going over a slow path
- **Topology-aware scheduling**: pods land on nodes connected to the same fast switch, not scattered across the rack

## Trade-offs

**What you keep**: your PyTorch or JAX training code.

**What you give up**: the assumption that you can just `torchrun` 32 ranks and it'll work. The platform has to know this is a distributed job and treat it as one.

## Try it

A working demonstration lives in [`examples/C04-multi-node/`](../examples/C04-multi-node/). Same distributed training simulation submitted two ways (bare Jobs vs PyTorchJob), runnable on a Mac with a local Kind cluster and no GPU required. The before case shows the rendezvous timeout and hang; the after case shows the operator coordinating all pods together and recovering a crashed worker without restarting the master.

---

[← Pain C.03: Can't express GPU config](C03-whole-gpus-only.md) · [Landscape](../README.md) · [Pain C.05: GPUs starve for data →](C05-data-starvation.md)
