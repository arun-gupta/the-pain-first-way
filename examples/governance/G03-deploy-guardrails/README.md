# Pain G.03 example: anything can deploy, and I can't prove who approved it

A working demonstration of [Pain G.03: Anything can deploy, and I can't prove who
approved it](../../../pains/governance/G03-deploy-guardrails.md). The same workload,
deployed into two clusters: one with no gate, one with a policy gate in front of it.
The manifest is the only thing that changes.

**Demonstrates:** Kyverno · admission control · policy-as-code

## The point of the diff

`before/` deploys `bad-deployment.yaml` into an ungoverned cluster. The image comes
from an unapproved registry, uses a mutable `:latest` tag, and carries no `owner` or
`data-residency` label. Nothing stops it. It runs, and "was it compliant, who
approved it" has no answer.

`after/` installs a Kyverno `ClusterPolicy` with three rules in Enforce mode. The
exact same manifest is now rejected at admission, with the rejection naming every
rule it broke. Only `good-deployment.yaml`, which meets all three rules, gets through,
and the gate records the result as a PolicyReport.

## What's here

```
before/
  bad-deployment.yaml    # unapproved registry, :latest tag, no governance labels
  README.md

after/
  install-kyverno.sh     # install the admission controller and wait for it
  deploy-guardrails.yaml # one ClusterPolicy, three Enforce-mode rules
  good-deployment.yaml   # approved registry, pinned tag, owner + residency labels
  README.md              # re-applies ../before/bad-deployment.yaml to show rejection
```

No GPU required. The workloads are trivial (`nginx`, `pause`); the cloud native
concept, gating every change at admission, is identical for a real model server.

## Run it

- [`before/README.md`](before/README.md) -- deploy the non-compliant workload into an
  ungoverned cluster and watch it sail in
- [`after/README.md`](after/README.md) -- install the gate, watch the same manifest
  get rejected, and deploy the compliant one

## Scope

This demonstrates the admission-control half of the pain: a policy gate that rejects
non-compliant workloads. The other half, an enforced approval path (GitOps plus
branch protection and RBAC segregation of duties), is a process gate rather than a
kubectl command and is described in the pain rather than demonstrated here.

---

[← Back to Pain G.03](../../../pains/governance/G03-deploy-guardrails.md) · [Landscape](../../../README.md) · [Examples index](../../README.md)
