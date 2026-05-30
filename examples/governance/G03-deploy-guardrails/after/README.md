# after/ -- a policy gate rejects what violates the rules

An admission policy ([Kyverno](https://kyverno.io/)) sits in front of the cluster.
Every Deployment is checked before it is created. The non-compliant manifest from
`before/` is now rejected, with the rejection naming each rule it broke, and only a
compliant Deployment gets through.

## Install the admission controller

From this directory:

```bash
./install-kyverno.sh
```

This applies the latest Kyverno release and waits until its admission controller is
ready. (It installs cluster-wide CRDs and an admission webhook, so it touches the
whole cluster, not just one namespace.)

## Apply the guardrails

```bash
kubectl apply -f deploy-guardrails.yaml
```

This creates one `ClusterPolicy`, `deploy-guardrails`, with three rules in Enforce
mode: an approved-registry rule, a no-`:latest` rule, and a required-labels rule
(`owner` and `data-residency`). Confirm it is in force:

```bash
kubectl get clusterpolicy
```

```
NAME                BACKGROUND   VALIDATE ACTION   READY
deploy-guardrails   true         Enforce           True
```

## The same manifest is now rejected

Try to deploy the exact non-compliant workload from `before/`:

```bash
kubectl apply -f ../before/bad-deployment.yaml
```

It never reaches the cluster. Admission rejects it and lists every rule it failed:

```
Error from server: error when creating "../before/bad-deployment.yaml": admission webhook "validate.kyverno.svc-fail" denied the request:

resource Deployment/default/payments-api was blocked due to the following policies

deploy-guardrails:
  disallow-latest-tag: 'validation error: A mutable '':latest'' tag is not allowed;
    pin an immutable version. rule disallow-latest-tag failed at path
    /spec/template/spec/containers/0/image/'
  require-approved-registry: 'validation error: Images must come from the approved
    registry ''registry.k8s.io''. rule require-approved-registry failed at path
    /spec/template/spec/containers/0/image/'
  require-governance-labels: 'validation error: Deployments must carry ''owner'' and
    ''data-residency'' labels. rule require-governance-labels failed at path
    /metadata/labels/'
```

One apply, three guardrails firing at once. The workload is not created, so the
cluster never holds a non-compliant payments service even briefly. (The doubled
single quotes are just how Kyverno's message is rendered as YAML; the text reads
`A mutable ':latest' tag is not allowed`.) If a `payments-api` already exists from an
earlier step, the same rules fire but the error reads `error when applying patch`
instead of `error when creating`, since the apply is updating it rather than creating
it.

Confirm nothing was admitted:

```bash
kubectl get deployment payments-api
```

```
Error from server (NotFound): deployments.apps "payments-api" not found
```

## The compliant manifest passes

`good-deployment.yaml` fixes all three: an `registry.k8s.io` image, a pinned tag, and
both governance labels.

```bash
kubectl apply -f good-deployment.yaml
kubectl rollout status deployment/payments-api
```

It is admitted and runs. The gate let it through because it met the policy, not by
luck.

## The gate left a record

Kyverno records the result of every check it ran as a PolicyReport, so the pass is
not just "it deployed," it is an artifact you can query:

```bash
kubectl get policyreport -o wide
```

```
NAME                                   KIND         NAME           PASS   FAIL   WARN   ERROR   SKIP   AGE
<report-id>                            Deployment   payments-api   3      0      0      0       0      30s
```

Look for the `payments-api` row: three rules checked, three passed, recorded against
the workload. Kyverno's background scan also evaluates Deployments that were already
in the cluster, so you may see extra rows here, and any that predate the policy and
violate it show up with a non-zero FAIL count. That is the scan surfacing existing
violators, not the gate failing: Enforce mode blocks new and changed deploys at
admission, but it reports on pre-existing ones rather than deleting them.

This is the cluster-side half of "who approved it": what the gate evaluated and
admitted. For a
durable, tamper-evident trail of who merged and approved the change in the first
place, see [Pain R.03: audit evidence](../../../../pains/compliance/R03-audit-evidence.md).

## Back to the questions

`before/` left an auditor's questions unanswerable on an ungoverned cluster. The gate
answers them:

- **Which registry did the image come from?** An approved one. `require-approved-registry`
  rejects anything not from `registry.k8s.io`.
- **What exactly is running?** A pinned version, not a moving target. `disallow-latest-tag`
  rejects `:latest`.
- **Who owns it, and where can its data live?** Stated on the workload.
  `require-governance-labels` requires `owner` and `data-residency`.
- **Who approved this deploy?** Half answered here: the PolicyReport records the gate's
  decision. The other half, the human who reviewed and approved the change, comes from
  the reviewed-merge path (GitOps plus branch protection and RBAC), which is described
  in the pain, not scripted in this demo.

## The point

In `before/`, the cluster accepted anything that parsed and could answer none of the
auditor's questions. Here, policy-as-code makes the rules explicit and enforces them
at the one chokepoint every change must pass. Non-compliant workloads are rejected
before they exist, compliant ones carry their owner and residency by construction,
and every decision is recorded.

Admission control is one half of the pain. The other half, that the cluster only
changes through a reviewed, approved merge (GitOps plus branch protection and RBAC
segregation of duties), is a process gate rather than a kubectl command, so it is
described in the [pain itself](../../../../pains/governance/G03-deploy-guardrails.md)
rather than demonstrated here. The two compose: the merge gate decides what is
allowed in, the admission gate enforces that nothing else can be.

## Beyond these three rules

This example uses one Kyverno capability, `validate` in Enforce mode, to reject
non-compliant Deployments. The same admission gate has other modes, each the
enforcement primitive behind a different pain in this guide. The install and the
`ClusterPolicy` shape stay the same; only the rule type changes.

- **Verify image signatures** (`verifyImages`): require that an image is signed and its
  provenance checks out before any pod runs, so an unsigned or tampered artifact is
  blocked at admission. This is the enforcement primitive behind [Pain F.02: loading a
  model can run code on my cluster](../../../../pains/foundation/F02-model-supply-chain.md),
  the natural next rule to add to a policy like this one.
- **Generate companion resources** (`generate`): when a namespace is created,
  automatically create a default-deny `NetworkPolicy`, a `ResourceQuota`, and baseline
  RBAC, so isolation exists by construction rather than by someone remembering. This is
  how [Pain R.02: one customer's workload can starve or leak into
  another](../../../../pains/compliance/R02-tenant-isolation.md) and [Pain A.04: a
  prompt-injected agent can call any endpoint](../../../../pains/agents/A04-agent-egress.md)
  get enforced per tenant.
- **Mutate on the way in** (`mutate`): fill in a safe default instead of rejecting, for
  example stamp an `owner` label or inject a non-root `securityContext`. The cooperative
  counterpart to the `validate` rules above.
- **Pin data to a region** (`validate` on labels plus node affinity): require a
  `data-residency` label and keep the workload on in-region nodes, the admission-control
  half of [Pain R.01: customer data can't leave their
  region](../../../../pains/compliance/R01-data-residency.md).

These are described, not scripted: this walkthrough stays focused on the three
`validate` rules so it runs end to end on a local Kind cluster with nothing to sign or
provision.

## Cleanup

This `ClusterPolicy` gates every Deployment on the cluster, not just this example's.
If you reuse this Kind cluster for other examples, delete the policy here, or those
workloads will be blocked too (anything from an unapproved registry or missing the
governance labels).

```bash
kubectl delete deployment payments-api --ignore-not-found
kubectl delete -f deploy-guardrails.yaml
```

To remove Kyverno itself as well:

```bash
kubectl delete -f https://github.com/kyverno/kyverno/releases/latest/download/install.yaml
```

---

[← Example index](../README.md)
