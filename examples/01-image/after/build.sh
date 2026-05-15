#!/usr/bin/env bash
# Build the image. With --push, also tag and push to Docker Hub.
#
# Usage:
#   bash build.sh           Build locally as embedder:latest
#   bash build.sh --push    Build, tag as <DOCKER_USERNAME>/embedder:latest, and push
#
# Push requires:
#   docker login -u <your-dockerhub-username>

set -euo pipefail

DOCKER_USERNAME="${DOCKER_USERNAME:-arun-gupta}"
IMAGE_NAME="${IMAGE_NAME:-embedder}"
TAG="${TAG:-latest}"

docker build -t "${IMAGE_NAME}:${TAG}" .
echo
echo "Built ${IMAGE_NAME}:${TAG}"

if [[ "${1:-}" == "--push" ]]; then
    REMOTE="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"
    docker tag "${IMAGE_NAME}:${TAG}" "${REMOTE}"
    docker push "${REMOTE}"
    echo
    echo "Pushed ${REMOTE}"
fi
