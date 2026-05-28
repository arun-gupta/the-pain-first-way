# After: RollingUpdate strategy with readiness probe

With `RollingUpdate` and a readiness probe, a bad push stalls before it becomes live. Old pods keep serving until new ones pass their health check. `kubectl rollout undo` reverts to the tracked previous revision.

Assumes you have already completed the one-time setup in [`../before/README.md`](../before/README.md):

- prerequisites installed
- Kind cluster created
- `./build.sh` already run from `examples/09-cant-roll-back/`

## 1. Switch to the after scenario

```bash
cd examples/09-cant-roll-back/after
```

## 2. Deploy v1

```bash
kubectl apply -f deployment-v1.yaml
kubectl apply -f service.yaml
kubectl rollout status deployment/model-server
```

Verify it serves traffic:

```bash
kubectl port-forward service/model-server 8080:80
```

In another terminal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
```

```
200
```

## 3. Push v2-bad

This is the real deployment action the pain is about: update the Deployment to point at a new image tag. `kubectl set image` patches the live Deployment in-place and records a new rollout revision. Here the new image is `model-server:v2-bad` — it starts a container, but that container never serves HTTP, so the readiness probe becomes the gate that protects traffic.

```bash
kubectl set image deployment/model-server server=model-server:v2-bad
kubectl get pods -w
```

```
NAME                           READY   STATUS    RESTARTS
model-server-5d4b9f-xkq        1/1     Running   0
model-server-5d4b9f-zrp        1/1     Running   0
model-server-7c8d2a-nwt        0/1     Running   0   ← new pod, readiness failing
```

The new pod starts but never becomes Ready. The two v1 pods keep serving.

```bash
kubectl rollout status deployment/model-server
```

```
Waiting for deployment "model-server" rollout to finish: 1 out of 2 new replicas have been updated...
```

The rollout is stalled — not falsely reporting success. Traffic is uninterrupted:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

```
200
```

## 4. Roll back

This reverts the Deployment to its previous rollout revision. Kubernetes updates the live Deployment spec back to `model-server:v1` and replaces the failed `v2-bad` attempt with the last known-good version.

```bash
kubectl rollout undo deployment/model-server
kubectl rollout status deployment/model-server
```

```
deployment "model-server" successfully rolled out
```

One command. No manifest required. The controller applied the tracked previous spec.

Check rollout history:

```bash
kubectl rollout history deployment/model-server
```

```
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

## Clean up

```bash
kubectl delete -f service.yaml
kubectl delete -f deployment-v1.yaml
```

---

[← Back to Pain 9](../../pains/09-cant-roll-back.md) · [Landscape](../../README.md) · [Examples index](../README.md)
