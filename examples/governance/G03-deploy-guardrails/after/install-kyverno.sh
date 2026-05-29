#!/usr/bin/env bash
# Install Kyverno (the admission controller) into the current cluster and wait
# until it is ready to gate deploys. Runs against whatever kubectl points at;
# for this walkthrough that is your local Kind cluster.
set -euo pipefail

echo "[install] applying Kyverno (latest release)..."
# Server-side apply is required: Kyverno's CRDs are larger than the 262144-byte
# limit on the last-applied-configuration annotation that a client-side apply uses.
kubectl apply --server-side --force-conflicts -f https://github.com/kyverno/kyverno/releases/latest/download/install.yaml

echo "[install] waiting for the admission controller to become ready..."
kubectl -n kyverno rollout status deploy/kyverno-admission-controller --timeout=180s

echo "[install] Kyverno is ready. Apply deploy-guardrails.yaml next."
