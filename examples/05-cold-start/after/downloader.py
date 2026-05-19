"""Init container entrypoint -- downloads model weights to a shared volume.

This script is the only thing that knows where the weights come from.
Swap it to change the source (S3, GCS, HuggingFace Hub, local file).
The server image never changes.

In this demo the "weights" are a local copy of weights.txt bundled with the
init container image. In a real deployment this script would use aws-cli,
gsutil, the HuggingFace hub client, or any other downloader.
"""
import os
import shutil
import sys
import time

# Destination is the shared emptyDir volume mounted at /model.
DEST = "/model/weights.txt"
# Source: in this demo, a local file bundled into the init container image.
# In a real deployment, replace this with an S3/GCS/HuggingFace download.
SOURCE = "/weights-source/weights.txt"


def download():
    os.makedirs(os.path.dirname(DEST), exist_ok=True)

    if not os.path.exists(SOURCE):
        print(f"[downloader] ERROR: source file not found: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    print(f"[downloader] Staging weights from {SOURCE} to {DEST} ...")
    start = time.time()
    shutil.copy2(SOURCE, DEST)
    elapsed = time.time() - start
    size = os.path.getsize(DEST)
    print(f"[downloader] Done in {elapsed:.3f}s ({size} bytes). Weights ready at {DEST}.")


if __name__ == "__main__":
    download()
