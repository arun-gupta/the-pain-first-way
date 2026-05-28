"""Naive training script -- no checkpointing.

Simulates 20 epochs of training with a fake loss curve.
Kill this process at any point and it restarts from epoch 0.
"""
import math
import time

TOTAL_EPOCHS = 20
SLEEP_PER_EPOCH = 3  # seconds -- long enough to observe, short enough to not wait forever


def fake_loss(epoch: int) -> float:
    """Deterministic fake loss: starts at 2.3, decays toward 0.1."""
    return 0.1 + 2.2 * math.exp(-0.25 * epoch)


def train():
    print(f"Starting training from epoch 0 (no checkpoint support)")
    for epoch in range(TOTAL_EPOCHS):
        time.sleep(SLEEP_PER_EPOCH)
        loss = fake_loss(epoch)
        print(f"epoch {epoch:>3}/{TOTAL_EPOCHS}  loss={loss:.4f}", flush=True)

    print("Training complete.")


if __name__ == "__main__":
    train()
