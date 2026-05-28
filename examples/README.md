# Examples

Runnable manifests, scripts, and starter code for each pain in the [field guide](../README.md).

Filled in pain-by-pain as the guide evolves. The goal: when you hit a pain, you can `kubectl apply` (or `helm install`, or `docker run`) something that demonstrates the pattern, not just read about it.

## Status

| # | Pain | Folder | Status |
|---|------|--------|--------|
| 1 | Model works locally, breaks in prod | [`01-image/`](01-image/) | Available |
| 2 | GPU job crashed at hour 14 | [`02-jobs/`](02-jobs/) | Available |
| 3 | Can't get a GPU | [`03-queueing/`](03-queueing/) | Available |
| 4 | Can't express GPU requirements (DRA) | [`04-whole-gpus-only/`](04-whole-gpus-only/) | Planned |
| 5 | Multi-node training | [`05-multi-node/`](05-multi-node/) | Available |
| 6 | Cold start | [`06-cold-start/`](06-cold-start/) | Available |
| 7 | Server image coupling | [`07-image-coupling/`](07-image-coupling/) | Available |
| 8 | GPU underutilization | [`08-gpu-underutilized/`](08-gpu-underutilized/) | Available |
| 9 | Can't roll back | [`09-cant-roll-back/`](09-cant-roll-back/) | Available |
| 10 | Latency spiked | `10-observability/` | Planned |
| 11 | Costs out of control | `11-autoscaling/` | Planned |
| 12 | Prompt version in prod | `12-config/` | Planned |
| 13 | Data residency | `13-multi-cluster/` | Planned |
| 14 | SLURM to Kubernetes (rewrite) | `14-slurm-migration/` | Planned |
| 15 | SLURM bridge (Slinky) | `15-slurm-bridge/` | Planned |
| 16 | Smart inference routing | `16-inference-routing/` | Planned |
| 17 | Serving many models | `17-serving-many-models/` | Planned |
| 18 | Weight-download stampede | `18-weight-stampede/` | Planned |
| 19 | GPUs starve for data | `19-data-starvation/` | Planned |
| 20 | Model supply chain | `20-model-supply-chain/` | Planned |
| 21 | GPU device health | `21-device-health/` | Planned |
| 22 | Quality gates | `22-quality-gates/` | Planned |
| 23 | Model reproducibility | `23-model-reproducibility/` | Planned |
| 24 | Durable agents | `24-durable-agents/` | Planned |
| 25 | Tenant isolation | `25-tenant-isolation/` | Planned |
| 26 | Model drift | `26-model-drift/` | Planned |
| 27 | Sandboxed code execution | `27-agent-sandbox/` | Planned |
| 28 | Tool and MCP fleet | `28-tool-fleet/` | Planned |
| 29 | Agent egress control | `29-agent-egress/` | Planned |
| 30 | Runaway-loop governance | `30-runaway-agents/` | Planned |

## Contributing an example

See [CONTRIBUTING.md](../CONTRIBUTING.md). Examples should be:

- **Minimal**: smallest manifest that demonstrates the pattern
- **Self-contained**: a folder per example, with its own README explaining what it shows and how to run it
- **Honest about limitations**: real-world deployments will need more

---

[Back to landscape](../README.md)
