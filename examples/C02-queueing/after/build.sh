#!/usr/bin/env bash
set -euo pipefail

CLUSTER=$(kind get clusters | head -1)
IMAGE="training-job:latest"

echo "Building $IMAGE ..."
docker build -t "$IMAGE" .

echo "Loading $IMAGE into Kind cluster '$CLUSTER' ..."
kind load docker-image "$IMAGE" --name "$CLUSTER"

echo "Done. Image is ready inside the cluster."
