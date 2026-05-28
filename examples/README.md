# Examples

Runnable manifests, scripts, and starter code for each pain in the [field guide](../README.md).

Filled in pain-by-pain as the guide evolves. The goal: when you hit a pain, you can `kubectl apply` (or `helm install`, or `docker run`) something that demonstrates the pattern, not just read about it.

## Status

| # | Pain | Folder | Status |
|---|------|--------|--------|
| F.01 | Model works locally, breaks in prod | [`01-image/`](01-image/) | Available |
| C.01 | GPU job crashed at hour 14 | [`02-jobs/`](02-jobs/) | Available |
| C.02 | Can't get a GPU | [`03-queueing/`](03-queueing/) | Available |
| C.03 | Can't express GPU requirements (DRA) | [`04-whole-gpus-only/`](04-whole-gpus-only/) | Planned |
| C.04 | Multi-node training | [`05-multi-node/`](05-multi-node/) | Available |
| S.01 | Cold start | [`06-cold-start/`](06-cold-start/) | Available |
| S.02 | Server image coupling | [`07-image-coupling/`](07-image-coupling/) | Available |
| O.01 | GPU underutilization | [`08-gpu-underutilized/`](08-gpu-underutilized/) | Available |
| S.03 | Can't roll back | [`09-cant-roll-back/`](09-cant-roll-back/) | Available |
| O.02 | Latency spiked | `10-observability/` | Planned |
| O.04 | Costs out of control | `11-autoscaling/` | Planned |
| G.01 | Prompt version in prod | `12-config/` | Planned |
| R.01 | Data residency | `13-multi-cluster/` | Planned |
| H.01 | SLURM to Kubernetes (rewrite) | `14-slurm-migration/` | Planned |
| H.02 | SLURM bridge (Slinky) | `15-slurm-bridge/` | Planned |
| S.05 | Smart inference routing | `16-inference-routing/` | Planned |
| S.06 | Serving many models | `17-serving-many-models/` | Planned |
| S.07 | Weight-download stampede | `18-weight-stampede/` | Planned |
| C.05 | GPUs starve for data | `19-data-starvation/` | Planned |
| F.02 | Model supply chain | `20-model-supply-chain/` | Planned |
| O.05 | GPU device health | `21-device-health/` | Planned |
| S.04 | Quality gates | `22-quality-gates/` | Planned |
| G.02 | Model reproducibility | `23-model-reproducibility/` | Planned |
| A.01 | Durable agents | `24-durable-agents/` | Planned |
| R.02 | Tenant isolation | `25-tenant-isolation/` | Planned |
| O.03 | Model drift | `26-model-drift/` | Planned |
| A.02 | Sandboxed code execution | `27-agent-sandbox/` | Planned |
| A.03 | Tool and MCP fleet | `28-tool-fleet/` | Planned |
| A.04 | Agent egress control | `29-agent-egress/` | Planned |
| A.05 | Runaway-loop governance | `30-runaway-agents/` | Planned |
| G.03 | Deploy guardrails | `31-deploy-guardrails/` | Planned |
| R.03 | Audit evidence | `32-audit-evidence/` | Planned |

## Contributing an example

See [CONTRIBUTING.md](../CONTRIBUTING.md). Examples should be:

- **Minimal**: smallest manifest that demonstrates the pattern
- **Self-contained**: a folder per example, with its own README explaining what it shows and how to run it
- **Honest about limitations**: real-world deployments will need more

---

[Back to landscape](../README.md)
