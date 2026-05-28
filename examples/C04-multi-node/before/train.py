"""Distributed training simulator — no GPU, no torch required.

Simulates a two-rank distributed training job using raw sockets for the
rendezvous step, mirroring what torch.distributed / NCCL does under the hood.

Environment variables (injected automatically by the Training Operator):
  RANK                  rank of this process (0 = master/coordinator)
  WORLD_SIZE            total number of ranks (default: 1)
  MASTER_ADDR           hostname of the rank-0 pod (default: localhost)
  MASTER_PORT           rendezvous port (default: 29500)
  RENDEZVOUS_TIMEOUT    seconds to wait for all peers (default: 60)

Demo-only variable (set in the *before* manifests to simulate slow pod start):
  WORKER_STARTUP_DELAY  seconds rank > 0 sleeps before attempting rendezvous
"""

import math
import os
import socket
import sys
import time

TOTAL_EPOCHS = 10
SLEEP_PER_EPOCH = 2

rank = int(os.environ.get("RANK", "0"))
world_size = int(os.environ.get("WORLD_SIZE", "1"))
master_addr = os.environ.get("MASTER_ADDR", "localhost")
master_port = int(os.environ.get("MASTER_PORT", "29500"))
rendezvous_timeout = int(os.environ.get("RENDEZVOUS_TIMEOUT", "60"))
worker_startup_delay = int(os.environ.get("WORKER_STARTUP_DELAY", "0"))


def fake_loss(epoch: int) -> float:
    """Deterministic fake loss: starts at 2.3, decays toward 0.1."""
    return 0.1 + 2.2 * math.exp(-0.25 * epoch)


def rendezvous_master() -> None:
    """Rank 0: open a server socket and wait for every other rank to connect."""
    print(
        f"[rank 0] Opening rendezvous on :{master_port}. "
        f"Waiting up to {rendezvous_timeout}s for {world_size - 1} worker(s) ...",
        flush=True,
    )
    workers: list[socket.socket] = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", master_port))
        srv.listen(world_size - 1)
        srv.settimeout(rendezvous_timeout)
        try:
            for _ in range(world_size - 1):
                conn, addr = srv.accept()
                workers.append(conn)
                print(f"[rank 0] Worker connected from {addr}", flush=True)
        except socket.timeout:
            print(
                f"[rank 0] RENDEZVOUS TIMEOUT: only {len(workers)}/{world_size - 1} "
                f"worker(s) showed up within {rendezvous_timeout}s.",
                flush=True,
            )
            print(
                "[rank 0] This is what an NCCL hang looks like: the collective "
                "blocks forever waiting for a peer that never arrives.",
                flush=True,
            )
            for conn in workers:
                conn.close()
            sys.exit(1)
        for conn in workers:
            conn.sendall(b"GO")
            conn.close()
    print(f"[rank 0] All {world_size} rank(s) ready. Starting distributed training.", flush=True)


def rendezvous_worker() -> None:
    """Rank > 0: optionally delay (demo device), then connect to master."""
    if worker_startup_delay > 0:
        print(
            f"[rank {rank}] Simulating slow start: sleeping {worker_startup_delay}s "
            "(represents a node still pulling the image or under memory pressure).",
            flush=True,
        )
        time.sleep(worker_startup_delay)

    print(
        f"[rank {rank}] Connecting to master at {master_addr}:{master_port} "
        f"(timeout: {rendezvous_timeout}s) ...",
        flush=True,
    )
    deadline = time.monotonic() + rendezvous_timeout
    while time.monotonic() < deadline:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((master_addr, master_port))
                data = s.recv(2)
                if data == b"GO":
                    print(
                        f"[rank {rank}] Rendezvous complete. Starting distributed training.",
                        flush=True,
                    )
                    return
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(2)

    print(
        f"[rank {rank}] RENDEZVOUS TIMEOUT: could not reach master at "
        f"{master_addr}:{master_port} within {rendezvous_timeout}s. Aborting.",
        flush=True,
    )
    sys.exit(1)


def train() -> None:
    for epoch in range(TOTAL_EPOCHS):
        time.sleep(SLEEP_PER_EPOCH)
        loss = fake_loss(epoch)
        print(f"[rank {rank}] epoch {epoch:>3}/{TOTAL_EPOCHS}  loss={loss:.4f}", flush=True)
    print(f"[rank {rank}] Training complete.", flush=True)


if __name__ == "__main__":
    print(
        f"[rank {rank}] Starting. WORLD_SIZE={world_size} "
        f"MASTER={master_addr}:{master_port}",
        flush=True,
    )
    if world_size == 1:
        print("[rank 0] Single-node mode (WORLD_SIZE=1). Skipping rendezvous.", flush=True)
    elif rank == 0:
        rendezvous_master()
    else:
        rendezvous_worker()

    train()
