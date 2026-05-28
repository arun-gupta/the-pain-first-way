# Before: RollingUpdate with no readiness probe

The default `RollingUpdate` strategy replaces pods in batches. Without a readiness probe, Kubernetes has no signal to distinguish a healthy pod from a broken one — any pod that starts counts as a successful rollout step. A bad push completes silently and bad pods receive traffic.

Assumes you have already completed the shared setup in [`../README.md`](../README.md):

- prerequisites installed
- Kind cluster created
- `./build.sh` already run from `examples/09-cant-roll-back/`

## 1. Switch to the before scenario

```bash
cd examples/09-cant-roll-back
cd before
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

This is the real deployment action the pain is about: update the Deployment to point at a new image tag. `kubectl set image` patches the live Deployment in-place and records a new rollout revision. Here the new image is `model-server:v2-bad` — it starts a container, but that container never serves HTTP.

```bash
kubectl set image deployment/model-server server=model-server:v2-bad
kubectl rollout status deployment/model-server
```

```
Waiting for deployment "model-server" rollout to finish: 1 out of 2 new replicas have been updated...
deployment "model-server" successfully rolled out
```

The rollout completed. Check the service:

```bash
curl http://localhost:8080
```

Expected result: the request fails. Depending on whether your existing port-forward is still attached to a broken pod or has already exited, you may see either of these:

```
curl: (52) Empty reply from server

curl: (7) Failed to connect to localhost port 8080 after 0 ms: Couldn't connect to server
```

The pods are Running, the rollout reported success, and the service is broken. Kubernetes gave no warning.

If you stop and restart the port-forward after this step, that fresh connection may fail with `connection refused`. That is still the same failure mode: the Service now points only at broken pods, so there is nothing healthy listening on port 80 behind it.

Why the port-forward can break: `kubectl port-forward` still has to connect to a real pod port behind the Service. After `kubectl set image` replaces `model-server:v1` with `model-server:v2-bad`, the new pods are `Running` but only executing `sleep 3600` — nothing is listening on port 80. An existing port-forward can die when its old v1 pod disappears, and a new port-forward can fail immediately when it lands on a v2-bad pod that refuses the connection.

## 4. Roll back

```bash
kubectl rollout undo deployment/model-server
kubectl rollout status deployment/model-server
```

`kubectl rollout undo` works here — but most teams don't know about it until after the first incident. The more common instinct is to dig through CI logs for the previous image tag and re-apply the old manifest.

After the rollback finishes, start the port-forward again:

```bash
kubectl port-forward service/model-server 8080:80
```

In another terminal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
```

Expected output:

```
200
```

## Clean up

```bash
kubectl delete -f service.yaml
kubectl delete -f deployment-v1.yaml
```

---

The [after/](../after/) folder shows how adding a readiness probe prevents the bad version from completing the rollout at all.
