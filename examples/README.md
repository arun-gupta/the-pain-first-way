# Examples

Runnable manifests, scripts, and starter code for each pain in the [field guide](../README.md).

Filled in pain-by-pain as the guide evolves. The goal: when you hit a pain, you can `kubectl apply` (or `helm install`, or `docker run`) something that demonstrates the pattern, not just read about it.

## Status

| # | Pain | Folder | Status |
|---|------|--------|--------|
| F.01 | Model works locally, breaks in prod | [`F01-image/`](F01-image/) | Available |
| C.01 | GPU job crashed at hour 14 | [`C01-jobs/`](C01-jobs/) | Available |
| C.02 | Can't get a GPU | [`C02-queueing/`](C02-queueing/) | Available |
| C.03 | Can't express GPU requirements (DRA) | [`C03-whole-gpus-only/`](C03-whole-gpus-only/) | Planned |
| C.04 | Multi-node training | [`C04-multi-node/`](C04-multi-node/) | Available |
| S.01 | Cold start | [`S01-cold-start/`](S01-cold-start/) | Available |
| S.02 | Server image coupling | [`S02-image-coupling/`](S02-image-coupling/) | Available |
| O.01 | GPU underutilization | [`O01-gpu-underutilized/`](O01-gpu-underutilized/) | Available |
| S.03 | Can't roll back | [`S03-cant-roll-back/`](S03-cant-roll-back/) | Available |
| O.02 | Latency spiked | `O02-observability/` | Planned |
| O.04 | Costs out of control | `O04-autoscaling/` | Planned |
| G.01 | Prompt version in prod | `G01-config/` | Planned |
| R.01 | Data residency | `R01-multi-cluster/` | Planned |
| H.01 | SLURM to Kubernetes (rewrite) | `H01-slurm-migration/` | Planned |
| H.02 | SLURM bridge (Slinky) | `H02-slurm-bridge/` | Planned |
| S.05 | Smart inference routing | `S05-inference-routing/` | Planned |
| S.06 | Serving many models | `S06-serving-many-models/` | Planned |
| S.07 | Weight-download stampede | `S07-weight-stampede/` | Planned |
| C.05 | GPUs starve for data | `C05-data-starvation/` | Planned |
| F.02 | Model supply chain | `F02-model-supply-chain/` | Planned |
| O.05 | GPU device health | `O05-device-health/` | Planned |
| S.04 | Quality gates | `S04-quality-gates/` | Planned |
| G.02 | Model reproducibility | `G02-model-reproducibility/` | Planned |
| A.01 | Durable agents | `A01-durable-agents/` | Planned |
| R.02 | Tenant isolation | `R02-tenant-isolation/` | Planned |
| O.03 | Model drift | `O03-model-drift/` | Planned |
| A.02 | Sandboxed code execution | `A02-agent-sandbox/` | Planned |
| A.03 | Tool and MCP fleet | `A03-tool-fleet/` | Planned |
| A.04 | Agent egress control | `A04-agent-egress/` | Planned |
| A.05 | Runaway-loop governance | `A05-runaway-agents/` | Planned |
| G.03 | Deploy guardrails | `G03-deploy-guardrails/` | Planned |
| R.03 | Audit evidence | `R03-audit-evidence/` | Planned |

## Contributing an example

See [CONTRIBUTING.md](../CONTRIBUTING.md). Examples should be:

- **Minimal**: smallest manifest that demonstrates the pattern
- **Self-contained**: a folder per example, with its own README explaining what it shows and how to run it
- **Honest about limitations**: real-world deployments will need more

---

[Back to landscape](../README.md)
