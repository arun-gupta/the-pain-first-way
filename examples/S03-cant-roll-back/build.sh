#!/usr/bin/env bash
# Build the rollout demo images and load them into Kind.
# Usage: ./build.sh [kind-cluster-name]
# Defaults to the active Kind cluster if no argument is given.

set -euo pipefail

CLUSTER="${1:-$(kind get clusters 2>/dev/null | head -1)}"

if [[ -z "${CLUSTER}" ]]; then
  echo "No Kind cluster found. Create one first with:"
  echo "  kind create cluster --name kind"
  exit 1
fi

build_and_load() {
  local image="$1"
  local context="$2"

  echo "==> Building ${image}"
  docker build -t "${image}" "${context}"

  echo "==> Loading ${image} into Kind cluster: ${CLUSTER}"
  kind load docker-image "${image}" --name "${CLUSTER}"
}

build_and_load "model-server:v1" "images/v1"
build_and_load "model-server:v2-bad" "images/v2-bad"

echo "==> Done. Demo images are ready in cluster '${CLUSTER}'."
echo "    Next:"
echo "      cd before   # or cd after"
echo "      kubectl apply -f deployment-v1.yaml"
echo "      kubectl apply -f service.yaml"
