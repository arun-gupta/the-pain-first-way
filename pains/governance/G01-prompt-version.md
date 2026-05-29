# Pain G.01: I can't tell which prompt version is in prod

> *A customer reports a regression on a specific kind of query. You suspect a prompt change from two weeks ago. The prompt lives partly in code, partly in a Notion doc, partly in a `.env` file on the prod box. Nobody can answer "what prompt was running on August 12th."*

## The pattern

Any value that affects behavior is config. In cloud native, config has a version, an owner, and a history. The prod environment doesn't have hidden state. What's running is what's in git.

## The primitives

- **ConfigMaps**: non-secret config (prompts, model names, feature flags) mounted into pods, versioned in git alongside the manifest
- **Image tags and digests**: every deploy references a specific image digest, so you can reproduce any past state
- **GitOps history**: the git log of your environment repo is your deployment audit trail; rollback is `git revert`

## Trade-offs

**What you keep**: your prompts and your prompt-engineering process. They move from scattered storage into a tracked file.

**What you give up**: editing a prompt in prod via the web UI. Prompt changes become PRs, which is annoying for about a week and load-bearing forever after.

---

[← Pain O.05: GPU device health](../operations/O05-device-health.md) · [Landscape](../../README.md) · [Pain G.02: Reproduce shipped model →](G02-model-reproducibility.md)
