# Pain 4: I asked for two GPUs and got two GPUs — but they can't talk to each other

> *Your workload needs two GPUs on the same high-speed interconnect for peer-to-peer memory transfers. You get two GPUs — but they're on different switches. Collective communication falls back to system RAM. Throughput drops 40%. You patch it with placement hints. It works until someone adds a node.*

## The pattern

The extended resource model treats all GPUs as interchangeable integers: `nvidia.com/gpu: 1` means "give me one GPU." That was sufficient when every workload needed one whole device. It breaks when you need a specific configuration:

- A partition of a GPU (a specific slice profile) rather than a whole device — for example, an NVIDIA MIG slice (`1g.10gb` vs `3g.40gb`) rather than a whole H100
- A GPU co-located with a specific network adapter on the same PCI switch, for high-bandwidth collective communication
- Two GPUs connected by a high-speed fabric for peer-to-peer memory transfers (NVLink on NVIDIA, Infinity Fabric on AMD)
- A fractional GPU for a small inference workload sharing a card with another tenant

The workaround is placement hints and custom labels that approximate what the scheduler should understand natively. Workloads land on the wrong topology. Partitioned GPU slices go unscheduled because the scheduler cannot express "give me this specific partition."

[Dynamic Resource Allocation (DRA)](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/) replaces the count-based model with structured resource claims.

## The primitives

**[Dynamic Resource Allocation (DRA)](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/)**: stable in Kubernetes 1.32 (KEP-3063), replaces the integer GPU count model with structured resource claims. A workload declares what it needs (`ResourceClaim`); a driver publishes what devices are available (`ResourceSlice`); the scheduler matches them with full topology awareness.

**[ResourceClaim](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/)**: a namespaced object a workload creates to request a specific device configuration. Replaces the `resources.limits` integer counter. The workload describes *what* it needs — a GPU partition of a particular profile, a GPU co-located with a specific NIC — not *which* device it wants.

**[DeviceClass](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/#deviceclass)**: a cluster-scoped object a cluster admin writes that defines a category of devices and any default configuration. A `ResourceClaim` references a `DeviceClass` to say "I need something from this category." Analogous to `StorageClass` for volumes.

**[ResourceSlice](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/#resourceslice)**: published by a vendor DRA driver (one per node) to advertise what devices are available. Contains structured attributes — slice profile, interconnect domain, PCI topology — that the scheduler can match against `ResourceClaim` constraints.

**A vendor DRA driver**: reads the physical GPU topology from the node (interconnect domains, partition profiles, PCI switch layout) and publishes it as `ResourceSlice` objects. Replaces the device plugin for clusters that need topology-aware placement. A pod that needs two interconnect-connected GPUs describes this in a `ResourceClaim`; the scheduler finds a node whose `ResourceSlice` contains two GPUs in the same interconnect domain and places the pod there. NVIDIA, AMD, and Intel each ship a DRA driver for their hardware.

**Migration path**: device plugins and DRA coexist. Existing workloads using integer GPU resources continue to work via the device plugin. New workloads that need topology-aware placement or GPU partitioning use DRA. Migration is per-workload, not cluster-wide.

## Trade-offs

**What you gain**: the scheduler understands your topology requirements natively instead of approximating them with labels and affinity rules. GPU partitions are first-class resources. Workloads land on the right hardware.

**What you give up**: operational simplicity. DRA requires Kubernetes 1.32 and a DRA-aware driver from your GPU vendor. Driver maturity varies across vendors — not all GPU configurations are supported. Debugging misplaced workloads shifts from "why didn't my placement hint match" to "why did the scheduler not find a matching ResourceSlice."

**Related**: Pain 3 covers scheduling fairness — getting *any* GPU when the cluster is contended. Pain 8 covers GPU *utilization* — making efficient use of the GPU once you have it. DRA is the scheduling primitive that makes Pain 3's priority classes and Pain 8's GPU partitioning work correctly at scale: you can queue and prioritize any GPU (Pain 3), but without DRA you cannot guarantee that partitioned GPUs (Pain 8) are claimed by the right workloads.

## Try it

Example coming soon. See [issue #21](https://github.com/arun-gupta/the-pain-first-way/issues/21) for what the example will cover.

---

[← Pain 3: Can't get a GPU](03-cant-get-a-gpu.md) · [Landscape](../README.md) · [Pain 5: Multi-node training →](05-multi-node-training.md)
