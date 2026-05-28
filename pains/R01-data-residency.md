# Pain R.01: Customer X's data can't leave their region

> *Enterprise sale closes on the condition that the customer's prompts, embeddings, and outputs never leave the EU. Your inference cluster is in us-east-1. You promise it'll be fine. It isn't.*

## The pattern

When data locality is a hard requirement, workloads run in the region where the data sits, with the network paths and access controls to prove it. Compliance becomes enforced by declarative policy, not only documented in a Confluence page.

## The primitives

- **Multi-cluster** (one cluster per region, or per customer): your control plane spans regions, your data planes don't
- **Namespace isolation with RBAC**: per-tenant boundaries inside a cluster, with bounded permissions
- **NetworkPolicies**: explicit allow-lists for which pods can talk to what; egress denied by default
- **External Secrets and KMS integration**: keys live in the customer's vault, not your image
- **Service mesh policies**: enforce mTLS, allowed destinations, and audit logging at the network layer

## Trade-offs

**What you keep**: your app. The fleet wraps it.

**What you give up**: a single global cluster as the default mental model. Some workloads have to live where the data lives.

---

[← Pain G.03: Deploy guardrails](G03-deploy-guardrails.md) · [Landscape](../README.md) · [Pain R.02: Tenant isolation →](R02-tenant-isolation.md)
