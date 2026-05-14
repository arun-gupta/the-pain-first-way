# Examples

Runnable manifests, scripts, and starter code for each pain in the [field guide](../README.md).

Filled in pain-by-pain as the guide evolves. The goal: when you hit a pain, you can `kubectl apply` (or `helm install`, or `docker run`) something that demonstrates the pattern, not just read about it.

## Status

| # | Pain | Folder | Status |
|---|------|--------|--------|
| 1 | Model works locally, breaks in prod | [`01-image/`](01-image/) | Available |
| 2 | GPU job crashed at hour 14 | `02-jobs/` | Planned |
| 3 | Can't get a GPU | `03-queueing/` | Planned |
| 4 | Multi-node training | `04-multi-node/` | Planned |
| 5 | Cold start | `05-cold-start/` | Planned |
| 6 | GPU underutilization | `06-utilization/` | Planned |
| 7 | Can't roll back | `07-rollouts/` | Planned |
| 8 | Latency spiked | `08-observability/` | Planned |
| 9 | Costs out of control | `09-autoscaling/` | Planned |
| 10 | Prompt version in prod | `10-config/` | Planned |
| 11 | Data residency | `11-multi-cluster/` | Planned |

## Contributing an example

See [CONTRIBUTING.md](../CONTRIBUTING.md). Examples should be:

- **Minimal**: smallest manifest that demonstrates the pattern
- **Self-contained**: a folder per example, with its own README explaining what it shows and how to run it
- **Honest about limitations**: real-world deployments will need more

---

[Back to landscape](../README.md)
