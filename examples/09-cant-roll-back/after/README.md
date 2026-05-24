# After: RollingUpdate strategy with readiness probe

**Prerequisites**: a Kubernetes cluster (Kind works fine — `kind create cluster`).

With `RollingUpdate` and a readiness probe, a bad push stalls before it becomes live. Old pods keep serving until new ones pass their health check. `kubectl rollout undo` reverts to the tracked previous revision.

## 1. Deploy v1

```bash
kubectl apply -f deployment-v1.yaml
kubectl rollout status deployment/model-server
```

Verify it serves traffic:

```bash
kubectl port-forward deployment/model-server 8080:80 &
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

```
200
```

## 2. Push v2-bad

```bash
kubectl apply -f deployment-v2-bad.yaml
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

## 3. Roll back

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
kill %1  # stop port-forward
kubectl delete -f deployment-v1.yaml
```

---

[← Back to Pain 9](../../pains/09-cant-roll-back.md) · [Landscape](../../README.md) · [Examples index](../README.md)
