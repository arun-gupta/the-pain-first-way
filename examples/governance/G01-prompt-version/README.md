# Pain G.01 example: which prompt version is in prod?

A working demonstration of [Pain G.01: I can't tell which prompt version is in prod](../../../pains/governance/G01-prompt-version.md). Same support-assistant server, two ways of handling the prompt that governs its behavior. The prompt is the only thing that changes.

**Demonstrates:** ConfigMap · Deployment revisions · GitOps rollback

## The point of the diff

`before/server.py` carries the prompt as a hardcoded constant that a `.env` file on
the box silently overrides. The prompt also (per the runbook) sometimes comes from a
Notion doc. There is no version, no owner, no history, and no endpoint that can tell
you what's actually running. "What prompt was live on August 12th?" is unanswerable.

`after/server.py` reads the prompt from a ConfigMap mounted at `/etc/prompt`,
versioned in git. The image carries no prompt. The pod reports its prompt version at
`/version`, `kubectl rollout history` records which version ran when, and rollback is
one `kubectl apply` (or one `git revert`).

## What's here

```
before/
  server.py          # prompt as a constant, silently overridden by .env
  .env.example       # stands in for the uncommitted override on the prod box
  README.md

after/
  server.py          # serving code only; reads prompt + version from /etc/prompt
  Dockerfile
  build.sh           # build prompt-server:v1 and load it into Kind
  configmap-v1.yaml  # prompt v1 (known good), version 2025-08-01-v1
  configmap-v2.yaml  # prompt v2 (the regression), version 2025-08-15-v2
  deployment.yaml    # mounts the ConfigMap, readiness probe, one constant image
  README.md
```

No GPU required. The inference is simulated; the cloud native concepts are identical
to a real model server.

## Run it

- [`before/README.md`](before/README.md) -- run bare with Python, watch the running prompt become a mystery
- [`after/README.md`](after/README.md) -- deploy v1, ship the v2 regression, answer "what's running," roll back

---

[← Back to Pain G.01](../../../pains/governance/G01-prompt-version.md) · [Landscape](../../../README.md) · [Examples index](../../README.md)
