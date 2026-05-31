# KubeCon NA 2026 CFP, Tutorial (75 min, hands-on)

Draft submission for the [companion guide](../README.md), as a hands-on tutorial: attendees run the guide's before/after examples themselves on a local Kind cluster. The standard ~35-minute session variant is in [kubecon-na-2026-session.md](kubecon-na-2026-session.md). Character limits per the CFP form are noted on each field.

## Title (max 70 characters)

Name the Pain, Run the Fix: Hands-On Cloud Native for AI Developers

Alternates:
- Run the Fix: A Hands-On Cloud Native Lab for AI Developers
- From Pain to Primitive, Live: Cloud Native Labs for AI Developers

## Abstract (max 1000 characters)

You hit a production pain, sense the fix is cloud native, but were never taught its vocabulary. In this tutorial you don't watch the fix, you run it. On your own laptop, a local Kind cluster with no GPU, you reproduce real pains and apply the cloud native primitive, before and after, feeling the difference yourself: an agent that charges a customer twice when it crashes mid-task, then exactly once; a deploy that sails in unchecked, then rejected at an admission gate; a bad change you roll back in one command. Each lab is a small, vendor-neutral pattern that maps to a CNCF project and pastes into your work the same week. We stay honest about scope: cloud native runs and enforces, it does not decide model quality. You leave with the patterns in muscle memory and a repo you have already run, plus the full catalog to keep working through after the room empties.

## Benefits to the Ecosystem (max 3000 characters)

Most cloud native onboarding assumes you already think in pods and Deployments. AI developers don't: they arrive from notebooks, training scripts, and SLURM, fluent in models but not in the platform now expected to run them. That gap slows adoption of the exact CNCF projects built to help them.

This tutorial closes the gap by making attendees do the work, not watch it. On a local Kind cluster, with no GPU and no image builds, each attendee runs a real production pain and its cloud native fix, before and after: an agent that charges a customer twice on a crash, then once; a non-compliant deploy that an admission gate rejects; a one-command rollback. They leave with the pattern in muscle memory and a repo they have already run on their own machine, not just slides they saw.

Every lab is vendor-neutral and maps to a real CNCF project, Deployments and Jobs, Kyverno for admission control, and a NATS JetStream queue or a database for durable agents, with no product pitch. Real AI stacks are never CNCF-only, so the labs show CNCF projects interoperating with the open-source tools teams already run, PostgreSQL behind durable agents and, in the broader guide, vLLM, Ray, Slurm, and Temporal, since no one project covers an AI stack end to end.

The barrier to follow along is deliberately low: stock images, code mounted from ConfigMaps, a one-command cluster setup, and committed expected-output for every lab, so an attendee whose cluster wedges can still keep pace and a reader can reproduce it later. It meets the audiences the ecosystem is courting, ML engineers and agent builders moving from notebooks to production, exactly where they are: at a terminal, running kubectl for maybe the first time.

It is honest about scope, drawing a clear line between what cloud native operates and enforces (covered) and what it does not decide, like model quality, eval, and prompts. The guide and every lab are open source under Apache-2.0, free to fork, extend, and reuse, and the full catalog, the lifecycle plus the HPC/Slurm on-ramp and the agent lane, lives in the same repo for self-study after the talk: https://github.com/arun-gupta/the-pain-first-way

## Prerequisites

Bring a laptop set up ahead of time (the repo has a pre-flight check; please run it before the session):

- Docker or Podman, [kind](https://kind.sigs.k8s.io/), and kubectl installed.
- Ability to create a local Kind cluster (one command; no GPU, no cloud account, no image builds).
- git, to clone https://github.com/arun-gupta/the-pain-first-way.
- Comfort with a terminal and basic kubectl. No prior Kubernetes experience assumed; the labs teach the vocabulary as you go.

Every lab ships committed expected-output, so attendees who hit setup trouble can still follow along and finish later.

## Track

**Cloud Native Novice.** A hands-on on-ramp for AI developers new to cloud native: it teaches the vocabulary by having them run it, which is the audience the whole guide serves.

## Level

**Beginner** (the form's Level options are Beginner, Advanced, or Any). No cloud native background assumed beyond running a container and a terminal. Audience: AI and ML developers, LLM app builders, and agent developers taking work from notebooks (or HPC and Slurm) into production.

## Format and logistics

A 75-minute hands-on tutorial: roughly 10 minutes to set up and verify, three before/after labs of about 18 minutes each that attendees run themselves, and a 5-minute wrap. Co-presenters or TAs circulate to unstick attendees; every lab has committed expected-output so anyone behind, or without a working cluster, can keep up. Best with a second presenter or one or two helpers for a full room.

## Additional Resources

The open-source guide and all runnable before/after examples: https://github.com/arun-gupta/the-pain-first-way

Lab plan (each lab is a before/after the attendee runs on their own Kind cluster):

0. Setup and verify (~10 min): create the Kind cluster, deploy the shared pieces, confirm with a health check.
1. The agent that won't stay alive (~18 min): run an in-memory agent, crash it mid-task, watch it charge the customer twice; then the durable variant (step state in Postgres, idempotent side effects) survives the same crash and charges once. Same crash again with a NATS JetStream queue that redelivers the work. (Pain A.01)
2. The deploy nobody approved (~18 min): apply a non-compliant workload to an open cluster and watch it sail in; install a Kyverno admission policy and watch the same manifest get rejected, with the decision recorded as a PolicyReport. (Pain G.03)
3. The change you can't roll back (~18 min): ship a bad version, then roll back in one command via Deployment revisions, with the history as an audit trail. (Pain S.03 / G.01)
4. Wrap (~5 min): the full catalog, the two on-ramps, and the honest boundary, for self-study.

## CNCF-hosted software

Projects attendees run in the labs (the broader guide references more; see the session submission and the repo):

- Kubernetes (Deployments, Jobs, ConfigMaps, Secrets, PVCs)
- Kyverno for policy and admission control (the admission-guardrails lab)
- NATS and NATS JetStream for durable work queues with redelivery (the durable-agent lab)
- Kind (Kubernetes SIG) for the local cluster every lab runs on

## Open source projects

Non-CNCF open source projects used in the labs:

- PostgreSQL (durable agent state and step checkpoints)
- Python (stock `python:3.12-slim`, with lab code mounted from ConfigMaps so there is nothing to build)

The full catalog also references Temporal, Apache Kafka, RabbitMQ, Pulsar, Redis Streams, vLLM, Ray, Slurm/Slinky, and more; see the session submission.
