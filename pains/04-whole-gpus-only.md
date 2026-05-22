# Pain 4: I need a specific GPU configuration but Kubernetes only knows how to count GPUs

> *Your inference workload needs two NVLink-connected GPUs for peer-to-peer memory transfers. Kubernetes places it on two GPUs that don't share a switch. NCCL falls back to system RAM. Training throughput drops 40%. You add node selectors to approximate the constraint. It works until someone adds a node.*

## The pattern

The extended resource model treats all GPUs as interchangeable integers: `nvidia.com/gpu: 1` means "give me one GPU." That was sufficient when every workload needed one whole device. It breaks when you need a specific configuration:

- A particular MIG slice (`1g.10gb` vs `3g.40gb`) rather than a whole H100
- A GPU paired with a specific RDMA NIC on the same PCI switch (for NCCL bandwidth)
- Two GPUs from the same NVLink domain (for peer-to-peer memory transfers)
- A fractional GPU for a small inference workload sharing a card with another tenant

The workaround is node selectors, affinity rules, and custom labels that approximate what the scheduler should understand natively. Workloads land on the wrong topology. MIG slices go unscheduled because the scheduler cannot express "give me this specific partition."

Dynamic Resource Allocation (DRA, KEP-3063, stable in Kubernetes 1.32) replaces the count-based model with structured resource claims. A workload declares what it needs (a `ResourceClaim`); a driver publishes what devices are available (a `ResourceSlice`); the scheduler matches them with full topology awareness.

## The primitives

**[ResourceClaim](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/)**: a namespaced object a workload creates to request a specific device configuration. Replaces the `resources.limits` integer counter. The workload describes *what* it needs — a MIG slice of a particular profile, a GPU co-located with a specific NIC — not *which* device it wants.

**[DeviceClass](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/#deviceclass)**: a cluster-scoped object a cluster admin writes that defines a category of devices and any default configuration. A `ResourceClaim` references a `DeviceClass` to say "I need something from this category." Analogous to `StorageClass` for volumes.

**[ResourceSlice](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/#resourceslice)**: published by a DRA driver (one per node) to advertise what devices are available. Contains structured attributes — MIG profile, NVLink domain, PCI topology — that the scheduler can match against `ResourceClaim` constraints. The NVIDIA DRA driver publishes one `ResourceSlice` per GPU node describing all MIG slices and their topology.

**The NVIDIA DRA driver**: reads the physical GPU topology from the node (NVLink domains, MIG profiles, PCI switch layout) and publishes it as `ResourceSlice` objects. Replaces the device plugin for clusters that need topology-aware placement. A pod that needs two NVLink-connected GPUs describes this in a `ResourceClaim`; the scheduler finds a node whose `ResourceSlice` contains two GPUs in the same NVLink domain and places the pod there.

**Migration path**: device plugins and DRA coexist. Existing workloads using `nvidia.com/gpu: 1` continue to work via the device plugin. New workloads that need topology-aware placement or MIG slices use DRA. Migration is per-workload, not cluster-wide.

## Trade-offs

**What you gain**: the scheduler understands your topology requirements natively instead of approximating them with labels and affinity rules. MIG slices are first-class resources. Workloads land on the right hardware.

**What you give up**: operational simplicity. DRA requires Kubernetes 1.32 and a DRA-aware driver. The NVIDIA DRA driver is under active development; not all GPU configurations are supported. Debugging misplaced workloads shifts from "why didn't my node selector match" to "why did the scheduler not find a matching ResourceSlice."

**Related**: Pain 3 covers scheduling fairness — getting *any* GPU when the cluster is contended. Pain 8 covers GPU *utilization* — making efficient use of the GPU once you have it. DRA is the scheduling primitive that makes Pain 3's priority classes and Pain 8's MIG partitioning work correctly at scale: you can queue and prioritize any GPU (Pain 3), but without DRA you cannot guarantee that MIG-partitioned GPUs (Pain 8) are claimed by the right workloads.

## Try it

Example coming soon. See [issue #21](https://github.com/arun-gupta/the-pain-first-way/issues/21) for what the example will cover.

---

[← Pain 3: Can't get a GPU](03-cant-get-a-gpu.md) · [Landscape](../README.md) · [Pain 5: Multi-node training →](05-multi-node-training.md)
