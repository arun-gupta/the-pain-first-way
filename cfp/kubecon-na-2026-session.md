# KubeCon NA 2026 CFP, Session (~35 min)

Draft submission for the [companion guide](../README.md), as a standard session: breadth, the catalog of pains, demo-driven. A hands-on **75-minute tutorial** variant is in [kubecon-na-2026-tutorial.md](kubecon-na-2026-tutorial.md). Character limits per the CFP form are noted on each field.

## Title (max 70 characters)

Name the Pain, Reach for the Fix: Cloud Native for AI Developers

Alternates:
- You Know the Pain. Cloud Native Is the Fix You Can't Name.
- From Pain to Primitive: Cloud Native for AI Developers
- Cloud Native, Pain-First: A Field Guide for AI Developers

## Abstract (max 1000 characters)

Inference at scale, multi-agent systems, and enterprise rollouts are tearing down the wall between experiment and system. AI developers hitting these pains sense the fix is cloud native but were never taught its vocabulary, so they cannot reach for it.

This talk is that vocabulary, pain-first. Not another Kubernetes tutorial: a catalog of real production pains, each starting from a problem you've hit, the GPU job that crashed at hour 14, the model you can't roll back, the agent that won't stay alive, then the cloud native primitive that solves it. Two paths into production, notebook-to-prod and HPC/Slurm-to-cloud-native, span the lifecycle from foundation to compliance, plus a dedicated lane for agent systems. Every pattern is vendor-neutral and maps to a CNCF project, and many ship as runnable before/after code. It is honest about scope: cloud native runs and enforces, it does not decide model quality or eval. You leave able to name what's biting you, and reach for the fix.

## Benefits to the Ecosystem (max 3000 characters)

Most cloud native onboarding assumes you already think in pods and Deployments. AI developers don't: they arrive from notebooks, training scripts, and SLURM, fluent in models but not in the platform now expected to run them. That gap slows adoption of the exact CNCF projects built to help them.

This talk closes the gap from the AI developer's side, and it does it with patterns, not slides. Each pain resolves to a reusable design pattern an attendee can apply at work the same week: a checkpoint-and-auto-restart training Job on a PersistentVolumeClaim that survives a crash at hour 14, gang scheduling with Kueue so multi-node jobs stop deadlocking, ConfigMap and Secret decoupling so one image serves every environment, rollback via Deployment revisions, and admission guardrails with Kyverno. Many ship as runnable before/after code, tested on a real GPU cluster and runnable locally on Kind, so the pattern is something you run, not just something you saw.

Attendees leave with three things: a vocabulary to name the pain and the cloud native primitive that fixes it, reusable vendor-neutral patterns to apply the same week, and a clear map of where cloud native's responsibility ends, so they reach for the right layer instead of expecting the platform to solve a model problem.

Everything is vendor-neutral and maps to real CNCF projects (Jobs and Kueue, DRA, KServe and the Gateway API Inference Extension, Kyverno) with no product pitch. Real AI stacks are never CNCF-only, so the patterns show those projects interoperating with the open-source tools teams already run, vLLM and Ray, Slurm from HPC, PostgreSQL and Temporal behind durable agents, since no one project covers an AI stack end to end. It also serves two audiences the ecosystem is actively courting: ML engineers moving from notebooks to production, and HPC teams weighing where Slurm and Kubernetes each fit as AI workloads pull them together.

Finally, it is honest about scope, drawing a clear line between what cloud native operates and enforces (covered) and what it does not decide, like model quality, eval, and prompts. The guide and all examples are open source under Apache-2.0, free to fork, extend, and reuse: https://github.com/arun-gupta/the-pain-first-way

## Track

**Cloud Native Novice.** The talk onboards AI developers who are new to cloud native, which matches the Beginner level and is the audience the whole guide serves. It spans the lifecycle rather than going deep on inference or agents alone, so it fits Novice better than the (also more crowded) AI Inference + Agentic track.

## Level

**Beginner** (the form's Level options are Beginner, Advanced, or Any). The talk assumes no cloud native background, you can build and run a container, not that you think in controllers and Deployments, and teaches the vocabulary pain-first. Audience: AI and ML developers, LLM app builders, and agent developers taking work from notebooks, or from HPC and Slurm, into production.

## Additional Resources

The open-source guide and all runnable before/after examples: https://github.com/arun-gupta/the-pain-first-way

Session outline (demo-driven, built from those examples):

1. The gap and the pain-first method: why a catalog of pains beats another Kubernetes tutorial.
2. Representative pains as live before/after runs: the GPU job that crashed at hour 14 (checkpoint Job on a PVC), the model you can't roll back (Deployment revisions), the agent that won't stay alive (durable execution on a queue or database).
3. The two on-ramps, notebook-to-prod and HPC/Slurm-to-cloud-native, and where each fits.
4. The honest boundary: what cloud native does not decide.
5. Where to take it next: the open-source guide and its runnable examples.

## CNCF-hosted software

Projects referenced or demonstrated in the talk that are hosted by CNCF (or are Kubernetes SIG subprojects):

- Kubernetes (Jobs, Deployments, ConfigMaps, Secrets, PVCs, DRA)
- Kueue (Kubernetes SIG-Scheduling) for gang scheduling and quotas
- KServe for model serving
- Kyverno for policy and admission control (deploy guardrails)
- KEDA for event-driven autoscaling
- Prometheus for inference and GPU observability
- Volcano for batch and gang scheduling
- Fluid for training-data orchestration
- Argo (Argo CD for GitOps rollout and history; Argo Workflows for durable agent execution)
- NATS and NATS JetStream for durable work queues with redelivery (agent durability)
- Strimzi for running Apache Kafka on Kubernetes (a durable-queue option)
- Gateway API and the Gateway API Inference Extension (Kubernetes SIG-Network)
- Knative for scale-to-zero serving
- node-problem-detector (Kubernetes SIG) for node and device health
- Kind (Kubernetes SIG) for running the examples locally
- Open Telemetry

## Open source projects

Non-CNCF open source projects referenced:

- vLLM (inference server)
- Slurm and Slinky (HPC scheduler and its Kubernetes bridge, SchedMD)
- NVIDIA GPU Operator and DCGM (GPU management and health)
- Ray and KubeRay (distributed compute)
- Sigstore / cosign (model supply-chain signing, OpenSSF)
- llm-d (KV-cache-aware inference routing)
- JuiceFS and Alluxio (data caching and acceleration)
- Spegel (peer-to-peer image and weight distribution)
- PostgreSQL (durable agent state and step checkpoints)
- Temporal (durable-execution engine for agent workflows)
- Apache Kafka, RabbitMQ, Apache Pulsar, Redis Streams (durable-queue options; Valkey is the open Redis fork)
- LangGraph (agent-framework state checkpointers)
