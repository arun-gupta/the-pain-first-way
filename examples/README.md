# Examples

Runnable manifests, scripts, and starter code for each pain in the [field guide](../README.md).

Filled in pain-by-pain as the guide evolves. The goal: when you hit a pain, you can `kubectl apply` (or `helm install`, or `docker run`) something that demonstrates the pattern, not just read about it.

## Status

| # | Pain | Folder | Status |
|---|------|--------|--------|
| 1 | Model works locally, breaks in prod | [`01-image/`](01-image/) | Available |
| 2 | GPU job crashed at hour 14 | [`02-jobs/`](02-jobs/) | Available |
| 3 | Can't get a GPU | [`03-queueing/`](03-queueing/) | Available |
| 4 | Multi-node training | [`04-multi-node/`](04-multi-node/) | Available |
| 5 | Cold start | [`05-cold-start/`](05-cold-start/) | Available |
| 6 | Server image coupling | [`06-image-coupling/`](06-image-coupling/) | Available |
| 7 | GPU underutilization | `07-utilization/` | Planned |
| 8 | Can't roll back | `08-rollouts/` | Planned |
| 9 | Latency spiked | `09-observability/` | Planned |
| 10 | Costs out of control | `10-autoscaling/` | Planned |
| 11 | Prompt version in prod | `11-config/` | Planned |
| 12 | Data residency | `12-multi-cluster/` | Planned |

## Contributing an example

See [CONTRIBUTING.md](../CONTRIBUTING.md). Examples should be:

- **Minimal**: smallest manifest that demonstrates the pattern
- **Self-contained**: a folder per example, with its own README explaining what it shows and how to run it
- **Honest about limitations**: real-world deployments will need more

---

[Back to landscape](../README.md)
