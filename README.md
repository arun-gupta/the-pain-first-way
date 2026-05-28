# The Pain-First Way: Cloud Native for AI Developers

Cloud native is the operating system for production software. AI development grew up parallel to it, mostly in notebooks and on rented GPU boxes. That's changed. Inference at scale, multi-agent systems, enterprise rollouts. The walls between an experiment and a system are coming down, and on the other side of those walls is a vocabulary AI developers haven't had to learn yet.

This guide is that vocabulary, pain-first. Each pain starts with a problem you've hit or are about to, names what's actually happening, and points at the cloud native primitive that solves it. Read in order, or jump to the one biting you this week.

What this guide is not: a Kubernetes tutorial. There are 500 of those. This is a translation between two worlds that increasingly need each other, with an honest accounting of where the translation runs out.

## Who this guide is for

AI developers whose work has outgrown a notebook:

- **ML engineers** shipping models from training to production
- **LLM app developers** serving inference at scale
- **Agent builders** running multi-step systems that fail in ways the notebook never did

Not the target audience: researchers who live in notebooks, data analysts, or MLOps engineers who already speak Kubernetes. You might still find parts of this useful sideways, but the guide assumes you're crossing from "trained a model" toward "operating a system," not coming the other direction.

## The pains

A growing catalog of pains across two on-ramps, notebook and HPC, and the production lifecycle from foundation to compliance. Click any pain to jump to it.

```mermaid
flowchart LR
    subgraph S1[Foundation]
        direction TB
        N1[✓ F.01 Model breaks in prod]
        N20[F.02 Model supply chain]
        N1 ~~~ N20
    end
    subgraph S2[Compute]
        direction TB
        N2[✓ C.01 GPU job crashed]
        N3[✓ C.02 Can't get a GPU]
        N4[C.03 Can't express GPU config]
        N5[✓ C.04 Multi-node falling over]
        N19[C.05 GPUs starve for data]
        N2 ~~~ N3
        N3 ~~~ N4
        N4 ~~~ N5
        N5 ~~~ N19
    end
    subgraph S3[Serving]
        direction TB
        N6[✓ S.01 Cold start]
        N7[✓ S.02 Server image coupling]
        N9[✓ S.03 Can't roll back]
        N22[S.04 Quality gates]
        N16[S.05 Inference routing]
        N17[S.06 Serving many models]
        N18[S.07 Weight stampede]
        N6 ~~~ N7
        N7 ~~~ N9
        N9 ~~~ N22
        N22 ~~~ N16
        N16 ~~~ N17
        N17 ~~~ N18
    end
    subgraph S4[Operations]
        direction TB
        N8[✓ O.01 GPU at 30 percent]
        N10[O.02 Latency spiked]
        N26[O.03 Model drift]
        N11[O.04 Costs out of control]
        N21[O.05 GPU device health]
        N8 ~~~ N10
        N10 ~~~ N26
        N26 ~~~ N11
        N11 ~~~ N21
    end
    subgraph S5[Governance]
        direction TB
        N12[G.01 Prompt version in prod]
        N23[G.02 Reproduce shipped model]
        N31[G.03 Deploy guardrails]
        N12 ~~~ N23
        N23 ~~~ N31
    end
    subgraph S6[Compliance]
        direction TB
        N13[R.01 Data residency]
        N25[R.02 Tenant isolation]
        N32[R.03 Audit evidence]
        N13 ~~~ N25
        N25 ~~~ N32
    end
    subgraph S7[Agent Systems]
        direction TB
        N24[A.01 Durable agents]
        N27[A.02 Sandboxed code exec]
        N28[A.03 Tool/MCP fleet]
        N29[A.04 Agent egress control]
        N30[A.05 Runaway-loop governance]
        N24 ~~~ N27
        N27 ~~~ N28
        N28 ~~~ N29
        N29 ~~~ N30
    end
    subgraph SHPC[Coming from HPC]
        direction TB
        N14[H.01 SLURM rewrite]
        N15[H.02 SLURM bridge]
        N14 ~~~ N15
    end
    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7
    SHPC ==> S2
    classDef avail fill:#bbf7d0,stroke:#16a34a,stroke-width:1px,color:#14532d;
    class N1,N2,N3,N5,N6,N7,N8,N9 avail;
    style SHPC fill:#fef3c7,stroke:#d97706,stroke-width:2px;
    linkStyle 30 stroke:#d97706,stroke-width:3px;
    click N1 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/F01-model-works-locally.md"
    click N2 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/C01-gpu-job-crashed.md"
    click N3 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/C02-cant-get-a-gpu.md"
    click N4 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/C03-whole-gpus-only.md"
    click N5 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/C04-multi-node-training.md"
    click N6 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S01-cold-start.md"
    click N7 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S02-server-image-coupling.md"
    click N8 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/O01-gpu-underutilized.md"
    click N9 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S03-cant-roll-back.md"
    click N10 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/O02-latency-spiked.md"
    click N11 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/O04-costs-out-of-control.md"
    click N12 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/G01-prompt-version.md"
    click N13 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/R01-data-residency.md"
    click N14 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/H01-slurm-migration.md"
    click N15 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/H02-slurm-bridge.md"
    click N16 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S05-inference-routing.md"
    click N17 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S06-serving-many-models.md"
    click N18 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S07-weight-stampede.md"
    click N19 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/C05-data-starvation.md"
    click N20 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/F02-model-supply-chain.md"
    click N21 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/O05-device-health.md"
    click N22 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/S04-quality-gates.md"
    click N23 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/G02-model-reproducibility.md"
    click N24 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/A01-durable-agents.md"
    click N25 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/R02-tenant-isolation.md"
    click N26 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/O03-model-drift.md"
    click N27 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/A02-agent-sandbox.md"
    click N28 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/A03-tool-fleet.md"
    click N29 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/A04-agent-egress.md"
    click N30 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/A05-runaway-agents.md"
    click N31 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/G03-deploy-guardrails.md"
    click N32 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/R03-audit-evidence.md"
```

**Legend:** ✓ (green) = a runnable before/after example exists today; unmarked = planned. The amber **Coming from HPC** path is an alternate on-ramp into Compute for teams migrating off SLURM.

## How to use this guide

Each pain is meant to be worked through end-to-end:

1. **Pick a pain.** The landscape diagram above links to each pain's page.
2. **Read the pattern and primitives.** What's actually happening, and the cloud native pieces that solve it.
3. **Try the example.** A runnable manifest demonstrating the primitives in action.

Examples live in [`examples/`](examples/) and are filled in pain-by-pain as the guide evolves. When a pain's example ships, the pain page links to it directly. See [examples/README.md](examples/README.md) for current status and to contribute one.

## The mental model shift

Before reading a pain, the reframe:

| From (your world) | To (cloud native) | The shift |
|---|---|---|
| Notebook kernel on your laptop | Pod: ephemeral, scheduled, identical to N others | Compute is interchangeable |
| `python serve.py` (an invocation) | Deployment: declared state of N replicas, platform keeps it true | Imperative becomes declarative |
| Local file on a disk you own | Volume: survives the pod, lives on infrastructure, mounted in | Storage outlives compute |
| `.env` with `HF_TOKEN` in plain text | Secret: scoped, rotated, audited | Secrets are first-class, not afterthoughts |
| "It works on my machine" | Container image: identical run, everywhere | The artifact is the contract |

The shift, in one line: invoke less, declare more.

## Reference

- [The Rosetta table](reference/rosetta-table.md): one-to-one mappings between your world and cloud native
- [CN primitives glossary](reference/cn-glossary.md): plain-language definitions for lower-level CN terms with no direct ML equivalent
- [Where cloud native doesn't help](reference/where-cn-doesnt-help.md): honest scope statement on what this guide doesn't cover
- [What not to translate](reference/what-not-to-translate.md): cloud native dogma that bends or breaks for AI workloads
- [Reading path](reference/reading-path.md): five things to actually touch, in order

## Contributing

Feedback, corrections, and additional pains welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Licensed under [Apache-2.0](LICENSE).
