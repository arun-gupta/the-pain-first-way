#!/usr/bin/env bash
# Build the prompt-server image and load it into Kind.
# Usage: ./build.sh [kind-cluster-name]
# Defaults to the active Kind cluster if no argument is given.

set -euo pipefail

CLUSTER="${1:-$(kind get clusters 2>/dev/null | head -1)}"

if [[ -z "${CLUSTER}" ]]; then
  echo "No Kind cluster found. Create one first with:"
  echo "  kind create cluster --name kind"
  exit 1
fi

IMAGE="prompt-server:v1"

echo "==> Building ${IMAGE}"
docker build -t "${IMAGE}" .

echo "==> Loading ${IMAGE} into Kind cluster: ${CLUSTER}"
kind load docker-image "${IMAGE}" --name "${CLUSTER}"

echo "==> Done. Next:"
echo "      kubectl apply -f configmap-v1.yaml"
echo "      kubectl apply -f deployment.yaml"
