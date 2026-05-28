# Before: RollingUpdate with no readiness probe

The default `RollingUpdate` strategy replaces pods in batches. Without a readiness probe, Kubernetes has no signal to distinguish a healthy pod from a broken one — any pod that starts counts as a successful rollout step. A bad push completes silently and bad pods receive traffic.

## 0. Navigate to this directory

```bash
cd examples/09-cant-roll-back/before
```

## Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

## 1. Create a Kind cluster

If you already have a Kind cluster named `kind` from a previous example, you can skip this step.

```bash
kind create cluster --name kind 2>/dev/null || echo "Cluster already exists, reusing it."
```

## 2. Deploy v1

```bash
kubectl apply -f deployment-v1.yaml
kubectl apply -f service.yaml
kubectl rollout status deployment/model-server
```

Verify it serves traffic:

```bash
kubectl port-forward service/model-server 8080:80 &
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

```
200
```

## 3. Push v2-bad

In practice this would be `kubectl set image deployment/model-server server=myrepo/model:v3`. Here we apply a new manifest to simulate the same effect:

```bash
kubectl apply -f deployment-v2-bad.yaml
kubectl rollout status deployment/model-server
```

```
Waiting for deployment "model-server" rollout to finish: 1 out of 2 new replicas have been updated...
deployment "model-server" successfully rolled out
```

The rollout completed. Check the service:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

```
curl: (52) Empty reply from server
```

The pods are Running, the rollout reported success, and the service is broken. Kubernetes gave no warning.

## 4. Roll back

```bash
kubectl rollout undo deployment/model-server
kubectl rollout status deployment/model-server
```

`kubectl rollout undo` works here — but most teams don't know about it until after the first incident. The more common instinct is to dig through CI logs for the previous image tag and re-apply the old manifest.

## Clean up

```bash
kill %1  # stop port-forward
kubectl delete -f service.yaml
kubectl delete -f deployment-v1.yaml
```

---

The [after/](../after/) folder shows how adding a readiness probe prevents the bad version from completing the rollout at all.
