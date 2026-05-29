# after/ -- the prompt is versioned config with an owner and a history

The prompt lives in a ConfigMap (`configmap-v1.yaml`), versioned in git. The server
image is constant and carries no prompt. The running pod can report which prompt
version it is serving, and swapping the prompt produces a Deployment revision you
can audit and roll back.

## Build the image into Kind

From this directory:

```bash
./build.sh
```

This builds `prompt-server:v1` and loads it into your Kind cluster.

## Deploy prompt v1

```bash
kubectl apply -f configmap-v1.yaml
kubectl apply -f deployment.yaml
kubectl annotate deployment/prompt-server kubernetes.io/change-cause="prompt 2025-08-01-v1" --overwrite
kubectl rollout status deployment/prompt-server
```

Step by step:

- **`apply configmap-v1.yaml`** creates the `system-prompt` ConfigMap holding the v1 prompt text and a `version` label. This is the single source of truth for the prompt, the thing that lives in git.
- **`apply deployment.yaml`** creates the Deployment. Its pods mount that ConfigMap at `/etc/prompt`, so the server reads the prompt from a file instead of baking it in.
- **`annotate ... change-cause=...`** records *what* this rollout was. Kubernetes stores it against the revision, so `kubectl rollout history` becomes a dated log of which prompt version was live, which is exactly the question `before/` couldn't answer.
- **`rollout status`** blocks until the new pods pass their readiness probe, so you don't query the server before it is ready.

Ask the pod what it is serving. The port-forward has to stay up for the rest of the
walkthrough, so give it its own terminal (if you ran the `before/` demo, stop that
server first so port 8080 is free).

**Terminal 1** -- the port-forward, leave it running:

```bash
kubectl port-forward deploy/prompt-server 8080:8080
```

`kubectl port-forward` is a direct debugging tunnel to one specific pod: even when
you point it at a Deployment, it picks a single pod at startup and stays bound to it.
It does not follow a rollout, so after each `rollout restart` below you will stop and
restart it (Ctrl+C, then re-run the command above) once the new pod is ready. Real
clients would not hit this: they reach the app through a Service, which always routes
to the current pods. The tunnel is just a convenience for poking one pod by hand.

**Terminal 2** -- run every command from here on, including the steps below:

```bash
curl localhost:8080/version
```

The response shows exactly what this pod is serving, version and all:

```
prompt_version: 2025-08-01-v1
prompt_sha256:  <hash>
prompt_text:    You are a helpful support assistant. End every answer with a ticket link.
```

## Ship the regression (prompt v2)

This is the change that "tweaked the prompt" two weeks later and dropped the
ticket-link instruction. In **Terminal 2**, apply the new prompt and roll it out:

```bash
kubectl apply -f configmap-v2.yaml
kubectl rollout restart deployment/prompt-server
kubectl annotate deployment/prompt-server kubernetes.io/change-cause="prompt 2025-08-15-v2" --overwrite
kubectl rollout status deployment/prompt-server
```

The rollout replaced the pod, so restart the port-forward to bind it to the new pod.
In **Terminal 1**, stop it with Ctrl+C and run:

```bash
kubectl port-forward deploy/prompt-server 8080:8080
```

Then query again in **Terminal 2**:

```bash
curl localhost:8080/version
```

It now reports `prompt_version: 2025-08-15-v2`. (If it still shows v1, the
port-forward is pointing at the old pod, restart it.)

## Answer the customer, then roll back

A customer reports the regression. Two questions that were unanswerable in `before/`,
both queries in **Terminal 2**.

What prompt versions have run, and when?

```bash
kubectl rollout history deployment/prompt-server
```

Each revision is tagged with the `change-cause` you annotated, so this is a dated log
of what was live:

```
REVISION  CHANGE-CAUSE
1         prompt 2025-08-01-v1
2         prompt 2025-08-15-v2
```

And what is the pod serving right now?

```bash
curl localhost:8080/version
```

```
prompt_version: 2025-08-15-v2
prompt_sha256:  <hash>
prompt_text:    You are a terse support assistant. Answer in one sentence.
```

Then roll back to the known-good prompt (an apply, in Terminal 2). Either re-apply v1:

```bash
kubectl apply -f configmap-v1.yaml
kubectl rollout restart deployment/prompt-server
kubectl rollout status deployment/prompt-server
```

or, in a GitOps repo, `git revert` the commit that introduced `configmap-v2.yaml`
and let the sync put v1 back.

This is another rollout, so restart the port-forward once more to reach the new pod.
In **Terminal 1**, stop it with Ctrl+C and run:

```bash
kubectl port-forward deploy/prompt-server 8080:8080
```

Then confirm with a query in **Terminal 2**:

```bash
curl localhost:8080/version
```

It reports `prompt_version: 2025-08-01-v1` again.

## The point

The prompt is config. Config has a version, an owner, and a history. The pod can
tell you what it is serving, the rollout history tells you what it served before,
and rollback is one command (or one revert). Nobody has to SSH a box to read a
`.env` ever again.

## Cleanup

Stop the port-forward with Ctrl+C in Terminal 1, then in Terminal 2:

```bash
kubectl delete deployment/prompt-server configmap/system-prompt
```

There is only one ConfigMap to delete: `configmap-v1.yaml` and `configmap-v2.yaml`
are two versions of the same object (`system-prompt`), so applying v2 updated it in
place rather than creating a second one.

---

[← Example index](../README.md)
