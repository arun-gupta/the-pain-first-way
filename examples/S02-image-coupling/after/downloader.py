"""Init container entrypoint -- downloads weights using config and credentials from the cluster.

Source URL comes from a ConfigMap (WEIGHTS_SOURCE env var).
Credentials come from a Secret (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY env vars).
Neither is in this image. Rotate the Secret or change the ConfigMap;
this container picks up the new values on the next pod start without any image rebuild.

In this demo the "download" is a local file copy to simulate a remote fetch.
In a real deployment, replace the shutil.copy2 call with aws s3 cp, gsutil cp,
or a HuggingFace hub download -- the env-var interface stays the same.
"""
import os
import shutil
import sys
import time

DEST = "/model/weights.txt"
SOURCE = "/weights-source/weights.txt"


def download():
    weights_source = os.environ.get("WEIGHTS_SOURCE")
    aws_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if not weights_source:
        print("[downloader] ERROR: WEIGHTS_SOURCE env var not set (expected from ConfigMap)", file=sys.stderr)
        sys.exit(1)
    if not aws_key_id or not aws_secret:
        print("[downloader] ERROR: AWS credentials not set (expected from Secret)", file=sys.stderr)
        sys.exit(1)

    print(f"[downloader] WEIGHTS_SOURCE={weights_source} (from ConfigMap)")
    print(f"[downloader] AWS_ACCESS_KEY_ID={aws_key_id[:8]}... (from Secret, not from image)")

    os.makedirs(os.path.dirname(DEST), exist_ok=True)

    if os.path.exists(DEST):
        size = os.path.getsize(DEST)
        print(f"[downloader] {DEST} already present ({size} bytes). Skipping download.")
        sys.exit(0)

    if not os.path.exists(SOURCE):
        print(f"[downloader] ERROR: source file not found: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    print(f"[downloader] Staging weights to {DEST} ...")
    start = time.time()
    shutil.copy2(SOURCE, DEST)
    elapsed = time.time() - start
    size = os.path.getsize(DEST)
    print(f"[downloader] Done in {elapsed:.3f}s ({size} bytes). Weights ready at {DEST}.")


if __name__ == "__main__":
    download()
