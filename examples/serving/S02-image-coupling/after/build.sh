#!/usr/bin/env bash
# Build the inference server image and load it into Kind.
# Usage: ./build.sh [kind-cluster-name]

set -euo pipefail

IMAGE="inference-server:latest"
CLUSTER="${1:-$(kind get clusters 2>/dev/null | head -1)}"

echo "==> Building $IMAGE"
docker build -t "$IMAGE" .

echo "==> Loading $IMAGE into Kind cluster: $CLUSTER"
kind load docker-image "$IMAGE" --name "$CLUSTER"

echo "==> Done. Image is ready in cluster '$CLUSTER'."
echo "    Next: kubectl apply -f configmap.yaml -f secret.yaml -f pod.yaml"
