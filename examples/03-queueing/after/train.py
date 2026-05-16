"""Training script with checkpoint save and resume.

Simulates 20 epochs of training. Writes a checkpoint after every epoch.
On restart, reads the checkpoint and resumes from where it left off.

Checkpoint lives at CHECKPOINT_PATH (default: /checkpoints/checkpoint.json).
When running in Kubernetes, that path is a mounted PersistentVolume.
When running locally, set CHECKPOINT_DIR env var to any writable directory.
"""
import json
import math
import os
import time
from pathlib import Path

TOTAL_EPOCHS = 20
SLEEP_PER_EPOCH = 3  # seconds
CHECKPOINT_DIR = Path(os.environ.get("CHECKPOINT_DIR", "/checkpoints"))
CHECKPOINT_FILE = CHECKPOINT_DIR / "checkpoint.json"


def fake_loss(epoch: int) -> float:
    """Deterministic fake loss: starts at 2.3, decays toward 0.1."""
    return 0.1 + 2.2 * math.exp(-0.25 * epoch)


def load_checkpoint() -> int:
    """Return the next epoch to run (0 if no checkpoint exists)."""
    if CHECKPOINT_FILE.exists():
        state = json.loads(CHECKPOINT_FILE.read_text())
        resume_epoch = state["epoch"] + 1
        print(
            f"Checkpoint found: epoch {state['epoch']} loss={state['loss']:.4f}. "
            f"Resuming from epoch {resume_epoch}.",
            flush=True,
        )
        return resume_epoch
    print("No checkpoint found. Starting from epoch 0.", flush=True)
    return 0


def save_checkpoint(epoch: int, loss: float) -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps({"epoch": epoch, "loss": loss}))


def train():
    start_epoch = load_checkpoint()

    if start_epoch >= TOTAL_EPOCHS:
        print("Training already complete (checkpoint says so).")
        return

    for epoch in range(start_epoch, TOTAL_EPOCHS):
        time.sleep(SLEEP_PER_EPOCH)
        loss = fake_loss(epoch)
        save_checkpoint(epoch, loss)
        print(f"epoch {epoch:>3}/{TOTAL_EPOCHS}  loss={loss:.4f}  (checkpoint saved)", flush=True)

    print("Training complete.")


if __name__ == "__main__":
    train()
