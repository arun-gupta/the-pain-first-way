# KubeCon NA 2026 CFP, Tutorial (75 min, hands-on)

Draft submission for the [companion guide](../README.md), as a hands-on tutorial: attendees run the guide's before/after examples themselves on a local Kind cluster. The standard ~35-minute session variant is in [kubecon-na-2026-session.md](kubecon-na-2026-session.md). Character limits per the CFP form are noted on each field.

## Title (max 70 characters)

Name the Pain, Run the Fix: Hands-On Cloud Native for AI Developers

Alternates:
- Run the Fix: A Hands-On Cloud Native Lab for AI Developers
- From Pain to Primitive, Live: Cloud Native Labs for AI Developers

## Abstract (max 1000 characters)

You hit a production pain, sense the fix is cloud native, but were never taught its vocabulary. This tutorial is hands-on with the real thing: live on a local Kind cluster (no GPU), we run each pain and its cloud native fix, before and after, so you feel the difference, an agent that charges a customer twice when it crashes mid-task then exactly once; a deploy that sails in unchecked then rejected at an admission gate; a bad change rolled back in one command. Bring a laptop and run it alongside, or just watch: every step is committed, so you can reproduce it the same day. Each lab is a small, vendor-neutral pattern that maps to a CNCF project and pastes into your work the same week. We stay honest about scope: cloud native runs and enforces, it does not decide model quality. You leave with the patterns and a repo built to run: a handful taught here, one per lifecycle stage, about two dozen more pains in the very same recipe, and a path to contribute your own.

## Benefits to the Ecosystem (max 3000 characters)

Most cloud native onboarding assumes you already think in pods and Deployments. AI developers don't: they arrive from notebooks, training scripts, and SLURM, fluent in models but not in the platform now expected to run them. That gap slows adoption of the exact CNCF projects built to help them.

This tutorial closes the gap by making attendees do the work, not watch it. On a local Kind cluster, with no GPU and no image builds, each attendee runs a real production pain and its cloud native fix, before and after: an agent that charges a customer twice on a crash, then once; a non-compliant deploy that an admission gate rejects; a one-command rollback. They leave with the pattern in muscle memory and a repo they have already run on their own machine, not just slides they saw.

A handful of labs, one per lifecycle stage, are enough to teach the recipe, name the pain, run the before, run the after, because that recipe repeats across the whole catalog: about two dozen more pains, many already shipping as runnable before/after examples and the rest open to build. Attendees leave able to keep going on their own, and the repo is set up to take their work back: bring a pain you have hit, add your own before/after, and it becomes part of the guide. That contribution path, not just consumption, is the durable ecosystem win.

Every lab is vendor-neutral and maps to a real CNCF project, Deployments and Jobs, Kyverno for admission control, and a NATS JetStream queue or a database for durable agents, with no product pitch. Real AI stacks are never CNCF-only, so the labs show CNCF projects interoperating with the open-source tools teams already run, PostgreSQL behind durable agents and, in the broader guide, vLLM, Ray, Slurm, and Temporal, since no one project covers an AI stack end to end.

The barrier to follow along is deliberately low: stock images, code mounted from ConfigMaps, a one-command cluster setup, and committed expected-output for every lab, so an attendee whose cluster wedges can still keep pace and a reader can reproduce it later. It meets the audiences the ecosystem is courting, ML engineers and agent builders moving from notebooks to production, exactly where they are: at a terminal, running kubectl for maybe the first time.

It is honest about scope, drawing a clear line between what cloud native operates and enforces (covered) and what it does not decide, like model quality, eval, and prompts. The guide and every lab are open source under Apache-2.0, free to fork, extend, and reuse, and the full catalog, the lifecycle plus the HPC/Slurm on-ramp and the agent lane, lives in the same repo for self-study after the talk: https://github.com/arun-gupta/the-pain-first-way

## Prerequisites

The tutorial is instructor-led, so **nothing is required to attend** beyond an interest in the topic; no prior Kubernetes experience is assumed, and the labs teach the vocabulary as we go.

To **follow along live** (optional, encouraged), bring a laptop with Docker or Podman, [kind](https://kind.sigs.k8s.io/), kubectl, and git, and run the repo's pre-flight check beforehand. Everything runs locally: no GPU, no cloud account, no image builds.

We do not depend on the room's setup or WiFi: every lab ships committed expected-output, so watching is a first-class path and anyone can reproduce the whole thing the same day from the repo.

## Track

**Cloud Native Novice.** A hands-on on-ramp for AI developers new to cloud native: it teaches the vocabulary by having them run it, which is the audience the whole guide serves.

## Level

**Beginner** (the form's Level options are Beginner, Advanced, or Any). No cloud native background assumed beyond running a container and a terminal. Audience: AI and ML developers, LLM app builders, and agent developers taking work from notebooks (or HPC and Slurm) into production.

## Format and logistics

A 75-minute, instructor-led hands-on tutorial: a short setup, then five before/after demos of about ten to twelve minutes each run live, one per lifecycle stage, and a 5-minute wrap. We run every step on a real Kind cluster on stage; attendees are welcome to run it alongside on a laptop, but it is not required. Committed expected-output for every lab means watching is a full experience and nothing hinges on the room's WiFi. A second presenter or a TA or two helps anyone who chooses to follow along on their own machine.

## Additional Resources

The open-source guide and all runnable before/after examples: https://github.com/arun-gupta/the-pain-first-way

Because it is instructor-led, the demos move at the presenter's pace, so the tutorial tours one pain per lifecycle stage rather than a single theme. Each is a before/after run live (attendees can follow along):

0. Setup and the recipe (~8 min): create the Kind cluster, deploy the shared pieces, and the pain-first method, name the pain, run the before, run the after.
1. Works locally, breaks in prod (~10 min): a server that runs on a laptop but dies in the cluster; a reproducible, pinned container image fixes it. (Pain F.01, foundation)
2. One image, every environment (~10 min): config and secrets baked into the image; decouple them into a ConfigMap and a Secret so the same image serves dev, staging, and prod. (Pain S.02, serving)
3. The change you can't roll back (~10 min): ship a bad version, then roll back in one command via Deployment revisions, with the history as an audit trail. (Pain S.03, serving)
4. The deploy nobody approved (~12 min): a non-compliant workload sails into an open cluster; a Kyverno admission policy rejects the same manifest and records the decision as a PolicyReport. (Pain G.03, governance)
5. The agent that won't stay alive (~12 min): an in-memory agent charges the customer twice on a crash; the durable variant (step state in Postgres, then a NATS JetStream queue that redelivers) survives and charges once. (Pain A.01, agent lane)
6. Wrap (~5 min): the same recipe across the rest of the catalog (about two dozen more pains), the two on-ramps and the honest boundary, and how to contribute your own.

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
