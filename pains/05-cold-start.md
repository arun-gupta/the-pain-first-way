# Pain 5: Cold start for my 70B model takes 4 minutes

> *A new replica (a running instance of your model server) needs to scale up. It pulls a 30GB image, downloads model weights from object storage, loads them into GPU memory, and warms the inference engine. Your users wait 4 minutes for the first response after a scale event.*

## The pattern

Each step in the startup sequence is sequential and slow. On a cold node with no cache, pulling a 30 GB image is slow even on high-speed networks; pull-through registries and node-local image caches reduce this, but without pre-warming, a new node still pays the full pull cost during a scale event, exactly when you need more replicas (running instances) up fast. Downloading 140 GB of FP16 weights from S3 or GCS adds another 2-3 minutes. Loading those weights into GPU memory is another 20-30 seconds. Engine warmup (JIT compilation, KV cache allocation) adds more on top. None of these steps overlap by default.

```mermaid
flowchart LR
    A[Server starts] --> B[Pull 30GB image<br/>~90s]
    B --> C[Download weights<br/>~120s]
    C --> D[Load to GPU<br/>~20s]
    D --> E[Engine warmup<br/>~10s]
    E --> F[Ready<br/>~4 min total]
```

Cold start hurts most when a traffic spike hits your model endpoint and capacity needs to expand fast, when your endpoint was idle and the first request has to wait for everything to load, or when you deploy a new model version and users hit timeouts during the switchover.

There are two axes of attack. On the model side: smaller models, quantized weights (INT8/INT4), and distilled variants all load faster because there is simply less data to move. A 7B INT4 model fits in ~4 GB; a 70B FP16 model needs ~140 GB. That is a 35x difference in load time before you change a single line of infra config. On the infrastructure side: keep ready capacity pre-warmed, split weight loading from image loading, and cache aggressively at every layer so subsequent scale events pay much less.

## The primitives

```mermaid
flowchart LR
    A2[Image cached on node<br/>DaemonSet · ~0s] --> B2[Weights on local volume<br/>PVC · ~5s] --> C2[Load to GPU<br/>~20s] --> D2[Engine warmup<br/>~10s] --> E2[Ready<br/>~35s]
    P1[Pre-pulled images] -.eliminates pull cost.-> A2
    P2[Node-local weight cache] -.eliminates download.-> B2
    P3[Warm pool<br/>minReplicas / KServe] -.skips all steps.-> F[Request served instantly]
```

- **Pre-pulled images on nodes**: A [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) — a Kubernetes workload that runs one pod on every node in the cluster — that references your model server image forces the runtime to cache its layers on every GPU node before it is needed. The next scale event finds the image already local and skips the 30 GB pull entirely.
- **PVCs and node-local caches**: Store model weights on a [PersistentVolume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) (PVC — a Kubernetes abstraction for durable storage that survives pod restarts) backed by fast local NVMe, or a shared ReadWriteMany volume (EFS, Filestore, Weka). Pods mount the volume instead of downloading weights at startup. The first pod on a node pays the download cost; every subsequent pod reads from local disk.
- **Init containers for weight staging**: An [init container](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) (a setup step that must complete before your model server starts) downloads weights into a shared volume before the inference process launches. This gives you three things: guaranteed sequencing (the server never starts with a partial model load), failure isolation (a bad download stops the pod before it serves a single request), and a clean separation between fetching logic and serving logic so you can swap downloaders (aws-cli, gcsfuse, HuggingFace hub) without rebuilding the server image.
- **Warm pools and minimum replicas**: Setting `minReplicas` above zero on an [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) (Horizontal Pod Autoscaler — Kubernetes' built-in scale-out controller) keeps at least one ready instance of your model server alive at all times. For predictable traffic patterns, pair it with [KEDA's CronScaler](https://keda.sh/docs/2.13/scalers/cron/) (a scheduled autoscaler that adds capacity on a time-based schedule, before traffic arrives) to pre-scale before known peak hours. The key is headroom: keep `minReplicas` one or two above your steady-state need so a traffic spike is absorbed while a cold instance is still initializing.
- **[KServe](https://kserve.github.io/website/) and serving-aware autoscalers** ([KEDA HTTP](https://github.com/kedacore/http-add-on), [Knative](https://knative.dev/docs/serving/)): these frameworks understand load-once, serve-many semantics. KServe's `InferenceService` supports a warm floor via `minReplicas` alongside optional scale-to-zero for cheaper models. It also holds incoming requests in a queue while a new pod initializes, so callers see latency rather than errors during a scale event.

## Trade-offs

**What you keep**: your model and your model server.

**What you give up**: scale-to-zero as a default. For big models, a 4-minute cold start is long enough to break SLAs and lose users; the math usually favors a warm floor. For small or quantized models (7B INT4 loads in under 30 seconds on NVMe), scale-to-zero is still viable and worth considering.

---

[← Pain 4: Multi-node training](04-multi-node-training.md) · [Landscape](../README.md) · [Pain 6: GPU underutilization →](06-gpu-underutilized.md)
