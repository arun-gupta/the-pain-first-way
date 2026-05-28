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

A growing catalog of pains, sequenced from foundation to compliance, plus newer pains not yet placed in the sequence. Click any pain to jump to it.

```mermaid
flowchart LR
    subgraph S1[Foundation]
        direction TB
        N1[1. Model breaks in prod]
    end
    subgraph S2[Compute]
        direction TB
        N2[2. GPU job crashed]
        N3[3. Can't get a GPU]
        N4[4. Can't express GPU config]
        N5[5. Multi-node falling over]
        N2 ~~~ N3
        N3 ~~~ N4
        N4 ~~~ N5
    end
    subgraph S3[Serving]
        direction TB
        N6[6. Cold start]
        N7[7. Server image coupling]
        N8[8. GPU at 30 percent]
        N9[9. Can't roll back]
        N10[10. Latency spiked]
        N6 ~~~ N7
        N7 ~~~ N8
        N8 ~~~ N9
        N9 ~~~ N10
    end
    subgraph S4[Operations]
        direction TB
        N11[11. Costs out of control]
    end
    subgraph S5[Governance]
        direction TB
        N12[12. Prompt version in prod]
    end
    subgraph S6[Compliance]
        direction TB
        N13[13. Data residency]
    end
    subgraph S7[Recently added · clustering pending]
        direction TB
        N14[14. SLURM rewrite]
        N15[15. SLURM bridge]
        N16[16. Inference routing]
        N17[17. Serving many models]
        N18[18. Weight stampede]
        N14 ~~~ N15
        N15 ~~~ N16
        N16 ~~~ N17
        N17 ~~~ N18
    end
    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7
    click N1 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/01-model-works-locally.md"
    click N2 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/02-gpu-job-crashed.md"
    click N3 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/03-cant-get-a-gpu.md"
    click N4 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/04-whole-gpus-only.md"
    click N5 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/05-multi-node-training.md"
    click N6 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/06-cold-start.md"
    click N7 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/07-server-image-coupling.md"
    click N8 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/08-gpu-underutilized.md"
    click N9 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/09-cant-roll-back.md"
    click N10 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/10-latency-spiked.md"
    click N11 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/11-costs-out-of-control.md"
    click N12 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/12-prompt-version.md"
    click N13 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/13-data-residency.md"
    click N14 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/14-slurm-migration.md"
    click N15 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/15-slurm-bridge.md"
    click N16 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/16-inference-routing.md"
    click N17 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/17-serving-many-models.md"
    click N18 "https://github.com/arun-gupta/the-pain-first-way/blob/main/pains/18-weight-stampede.md"
```

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
