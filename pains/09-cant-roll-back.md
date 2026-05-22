# Pain 9: I can't roll back a bad model without downtime

> *You pushed v3 of your model. p99 doubled and accuracy on your top intent dropped 4 points. Reverting means SSHing into N boxes, hoping the previous binary is still there, and praying nothing is half-deployed.*

## The pattern

In cloud native, deployment is a controlled state transition rather than an imperative script. Old replicas keep serving until new ones prove healthy. Rollback is reverting the declared state rather than re-running the install script.

## The primitives

- **Deployment**: declares "I want N replicas of this image with these resources"; the controller makes reality match
- **Rolling update**: replaces pods in batches, only after each new one passes a health check
- **Canary and blue-green** (Argo Rollouts, Flagger): route 5% of traffic to v3, watch metrics, ramp or revert

## Trade-offs

**What you keep**: your model server. The Deployment is a YAML manifest wrapping it.

**What you give up**: deploying as a verb you do. Deployment becomes a state you declare, and the platform converges to it.

---

[← Pain 8: GPU underutilization](08-gpu-underutilized.md) · [Landscape](../README.md) · [Pain 10: Latency spiked →](10-latency-spiked.md)
