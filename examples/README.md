# Examples

Runnable manifests, scripts, and starter code for each pain in the [field guide](../README.md).

Filled in pain-by-pain as the guide evolves. The goal: when you hit a pain, you can `kubectl apply` (or `helm install`, or `docker run`) something that demonstrates the pattern, not just read about it.

## Status

| # | Pain | Folder | Status |
|---|------|--------|--------|
| F.01 | Model works locally, breaks in prod | [`foundation/F01-image/`](foundation/F01-image/) | Available |
| C.01 | GPU job crashed at hour 14 | [`compute/C01-jobs/`](compute/C01-jobs/) | Available |
| C.02 | Can't get a GPU | [`compute/C02-queueing/`](compute/C02-queueing/) | Available |
| C.03 | Can't express GPU requirements (DRA) | [`compute/C03-whole-gpus-only/`](compute/C03-whole-gpus-only/) | Planned |
| C.04 | Multi-node training | [`compute/C04-multi-node/`](compute/C04-multi-node/) | Available |
| S.01 | Cold start | [`serving/S01-cold-start/`](serving/S01-cold-start/) | Available |
| S.02 | Server image coupling | [`serving/S02-image-coupling/`](serving/S02-image-coupling/) | Available |
| O.01 | GPU underutilization | [`operations/O01-gpu-underutilized/`](operations/O01-gpu-underutilized/) | Available |
| S.03 | Can't roll back | [`serving/S03-cant-roll-back/`](serving/S03-cant-roll-back/) | Available |
| O.02 | Latency spiked | `operations/O02-observability/` | Planned |
| O.04 | Costs out of control | `operations/O04-autoscaling/` | Planned |
| G.01 | Prompt version in prod | [`governance/G01-prompt-version/`](governance/G01-prompt-version/) | Available |
| R.01 | Data residency | `compliance/R01-multi-cluster/` | Planned |
| H.01 | SLURM to Kubernetes (rewrite) | `hpc/H01-slurm-migration/` | Planned |
| H.02 | SLURM bridge (Slinky) | `hpc/H02-slurm-bridge/` | Planned |
| S.05 | Smart inference routing | `serving/S05-inference-routing/` | Planned |
| S.06 | Serving many models | `serving/S06-serving-many-models/` | Planned |
| S.07 | Weight-download stampede | `serving/S07-weight-stampede/` | Planned |
| C.05 | GPUs starve for data | `compute/C05-data-starvation/` | Planned |
| F.02 | Model supply chain | `foundation/F02-model-supply-chain/` | Planned |
| O.05 | GPU device health | `operations/O05-device-health/` | Planned |
| S.04 | Quality gates | `serving/S04-quality-gates/` | Planned |
| G.02 | Model reproducibility | `governance/G02-model-reproducibility/` | Planned |
| A.01 | Durable agents | `agents/A01-durable-agents/` | Planned |
| R.02 | Tenant isolation | `compliance/R02-tenant-isolation/` | Planned |
| O.03 | Model drift | `operations/O03-model-drift/` | Planned |
| A.02 | Sandboxed code execution | `agents/A02-agent-sandbox/` | Planned |
| A.03 | Tool and MCP fleet | `agents/A03-tool-fleet/` | Planned |
| A.04 | Agent egress control | `agents/A04-agent-egress/` | Planned |
| A.05 | Runaway-loop governance | `agents/A05-runaway-agents/` | Planned |
| G.03 | Deploy guardrails | `governance/G03-deploy-guardrails/` | Planned |
| R.03 | Audit evidence | `compliance/R03-audit-evidence/` | Planned |

## Contributing an example

See [CONTRIBUTING.md](../CONTRIBUTING.md). Examples should be:

- **Minimal**: smallest manifest that demonstrates the pattern
- **Self-contained**: a folder per example, with its own README explaining what it shows and how to run it
- **Explicit about tech**: open the README with a `**Demonstrates:**` line naming the cloud native technologies it shows (see the [master list](https://github.com/arun-gupta/the-pain-first-way/issues/31))
- **Honest about limitations**: real-world deployments will need more

---

[Back to landscape](../README.md)
