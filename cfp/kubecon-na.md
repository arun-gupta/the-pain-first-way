# KubeCon NA CFP Submission

Draft submission for the [companion guide](../README.md). Character limits per the CFP form are noted on each field.

## Title (max 70 characters)

Cloud Native, Pain-First: A Field Guide for AI Developers

Alternates:
- From Notebook to Production: Cloud Native for AI, Pain-First
- Two On-Ramps to Production: A Pain-First Cloud Native Guide

## Abstract (max 1000 characters)

Inference at scale, multi-agent systems, and enterprise rollouts are tearing down the wall between an experiment and a system, and on the other side is a vocabulary AI developers were never made to learn.

This talk is that vocabulary, pain-first. Not another Kubernetes tutorial: a catalog of real production pains, each starting from a problem you've hit, the GPU job that crashed at hour 14, the model you can't roll back, the agent that won't stay alive, then the cloud native primitive that solves it. Two paths into production, notebook-to-prod and HPC/Slurm-to-cloud-native, span the lifecycle: foundation, compute, serving, operations, governance, and compliance, plus a dedicated lane for agent systems. Every pattern is vendor-neutral and maps to a CNCF project, and many ship as runnable before/after code. It is honest about scope: cloud native runs and enforces, it does not decide model quality or eval. You leave able to name what's biting you, and what to reach for.

## Benefits to the Ecosystem (max 2000 characters)

Most cloud native onboarding assumes you already think in pods and Deployments. AI developers don't: they arrive from notebooks, training scripts, and SLURM, fluent in models but not in the platform now expected to run them. That gap slows adoption of the exact CNCF projects built to help them.

This talk closes the gap from the AI developer's side, and it does it with patterns, not slides. Each pain resolves to a reusable design pattern an attendee can apply at work the same week: a checkpoint-and-auto-restart training Job on a PersistentVolumeClaim that survives a crash at hour 14, gang scheduling with Kueue so multi-node jobs stop deadlocking, ConfigMap and Secret decoupling so one image serves every environment, rollback via Deployment revisions, and admission guardrails with Kyverno. Many ship as runnable before/after code, tested on a real GPU cluster and runnable locally on Kind, so the pattern is something you run, not just something you saw.

Everything is vendor-neutral and maps to real CNCF projects (Jobs and Kueue, DRA, KServe and the Gateway API Inference Extension, Kyverno) with no product pitch. Real AI stacks are never CNCF-only, so the patterns show those projects interoperating with the open-source tools teams already run, vLLM and Ray, Slurm from HPC, PostgreSQL and Temporal behind durable agents, because the ecosystem's collective power beats any single project. It also serves two audiences the ecosystem is actively courting: ML engineers moving from notebooks to production, and HPC teams weighing where Slurm and Kubernetes each fit as AI workloads pull them together.

Finally, it is honest about scope, drawing a clear line between what cloud native operates and enforces (covered) and what it does not decide, like model quality, eval, and prompts. The guide and all examples are open source under Apache-2.0, a durable resource the community can extend long after the talk: https://github.com/arun-gupta/the-pain-first-way

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
