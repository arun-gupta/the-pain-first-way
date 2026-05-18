#!/usr/bin/env bash
# Build the distributed-training image and load it into Kind.
# Usage: ./build.sh [kind-cluster-name]
# Defaults to the active Kind cluster if no argument is given.
#
# Run this once before trying the before/ demo. The after/ example uses
# the same image — no rebuild needed when you move there.

set -euo pipefail

IMAGE="dist-training:latest"
CLUSTER="${1:-$(kind get clusters 2>/dev/null | head -1)}"

echo "==> Building $IMAGE"
docker build -t "$IMAGE" .

echo "==> Loading $IMAGE into Kind cluster: $CLUSTER"
kind load docker-image "$IMAGE" --name "$CLUSTER"

echo "==> Done. Image is ready in cluster '$CLUSTER'."
echo "    Next: kubectl apply -f dist-job.yaml"
