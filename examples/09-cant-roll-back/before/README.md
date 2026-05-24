# Before: Recreate strategy, no readiness probe

**Prerequisites**: a Kubernetes cluster (Kind works fine — `kind create cluster`).

With `Recreate`, all existing pods are terminated before new ones start. Without a readiness probe, the Deployment considers a pod ready as soon as it is Running — regardless of whether it serves traffic.

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
NAME                           READY   STATUS        RESTARTS
model-server-5d4b9f-xkq        1/1     Terminating   0
model-server-5d4b9f-zrp        1/1     Terminating   0
model-server-7c8d2a-nwt        0/1     Running       0
model-server-7c8d2a-pvs        0/1     Running       0
```

All v1 pods terminated before v2 started — the service was unavailable during the gap. The new pods show `Running` but sleep instead of serving HTTP.

```bash
kubectl rollout status deployment/model-server
```

```
deployment "model-server" successfully rolled out
```

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

```
curl: (52) Empty reply from server
```

The Deployment reports success. The service is broken. No warning was given.

## 3. Roll back

```bash
kubectl apply -f deployment-v1.yaml
```

Manual re-apply of the previous manifest. This works here because the file is still present. On a real cluster, the previous version may be a CI artifact from a pipeline run three weeks ago.

## Clean up

```bash
kill %1  # stop port-forward
kubectl delete -f deployment-v1.yaml
```

---

The [after/](../after/) folder shows how a readiness probe and `RollingUpdate` prevent the bad version from ever becoming live.
