#!/usr/bin/env bash
# Build the training image and load it into Kind.
# Usage: ./build.sh [kind-cluster-name]
# Defaults to the active Kind cluster if no argument is given.

set -euo pipefail

IMAGE="training-job:latest"
CLUSTER="${1:-$(kind get clusters 2>/dev/null | head -1)}"

echo "==> Building $IMAGE"
docker build -t "$IMAGE" .

echo "==> Loading $IMAGE into Kind cluster: $CLUSTER"
kind load docker-image "$IMAGE" --name "$CLUSTER"

echo "==> Done. Image is ready in cluster '$CLUSTER'."
echo "    Apply the manifests:"
echo "      kubectl apply -f pvc.yaml"
echo "      kubectl apply -f job.yaml"
