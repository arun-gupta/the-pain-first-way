# before/ -- an ungoverned cluster admits anything that parses

There is no gate. Any Deployment that is valid YAML reaches the cluster, compliant
or not. `bad-deployment.yaml` violates three rules a regulated team would care about,
and nothing stops it.

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

No Docker or image build is needed: this example uses public images. The same Kind
cluster is reused by `after/`, so set it up once here.

## Create a Kind cluster

If you already have a Kind cluster named `kind` from a previous example, you can skip
this step.

```bash
kind create cluster --name kind 2>/dev/null || echo "Cluster already exists, reusing it."
```

## Deploy the non-compliant workload

`bad-deployment.yaml` is a `payments-api` Deployment with three things wrong with it,
each one something a regulated team would want blocked:

- its image is `nginx:latest`, pulled from an unapproved public registry (docker.io)
- the `:latest` tag is mutable, so what actually runs can change without the manifest
  changing
- it carries no `owner` and no `data-residency` label, so nothing records who is
  accountable for it or where its data is allowed to live

Apply it:

```bash
kubectl apply -f bad-deployment.yaml
kubectl rollout status deployment/payments-api
```

It is admitted and runs anyway. Confirm it is live:

```bash
kubectl get deployment payments-api
```

```
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
payments-api   1/1     1            1           10s
```

## The questions nobody can answer

This workload is in prod, and none of those three problems was checked on the way in.
So the questions an auditor asks land on a cluster that kept no answers:

- **Which registry did the image come from?** Nothing required an approved source.
- **What exactly is running?** A `:latest` tag, so even the image is a moving target.
- **Who owns it, and where can its data live?** No labels, so nobody is on record as
  accountable.
- **Who approved this deploy?** Nothing gated it, so there is no enforced approval and
  no record that one happened.

The cluster enforced none of this because nothing was asked of it. The workload is
compliant or not by luck, and "who said yes" has no answer.

## Clean up before moving on

Delete it so the gate in `after/` sees a fresh create, not an update to something
that already slipped in:

```bash
kubectl delete deployment payments-api
```

Then continue to [`../after/README.md`](../after/README.md), where the same manifest
is rejected at admission.

---

[← Example index](../README.md)
