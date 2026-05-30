"""after-queue/: a durable queue holds the task and redelivers it on crash (option C).

The worker pulls a task from a NATS JetStream stream, runs it, and acks only on
success. If it crashes before the ack, JetStream redelivers the whole work item to a
new worker after the ack-wait window. There is no per-step checkpoint here: the queue
knows only "acked or not", so the redelivered worker reprocesses every step. The stable
idempotency key is what keeps the charge at exactly one.
"""
import asyncio
import os

import nats
from nats.js.api import ConsumerConfig

import agent_task

NATS_URL = os.environ.get("NATS_URL", "nats://nats:4222")
STREAM = "tasks"
SUBJECT = "tasks.run"
DURABLE = "worker"
# Redelivery happens ack_wait after a message is delivered, so this is roughly how long
# after a crash the task is retried. It must stay larger than the task itself (~8s with
# STEP_DELAY=2) or a healthy run would be redelivered before it finishes.
ACK_WAIT_SECONDS = 15


class QueueStore:
    """The queue provides part 1 (the work item) and part 3 (redelivery). It tracks no
    per-step progress, so nothing is ever "already done": a redelivery reprocesses the
    whole task, and only the stable key (part 2) prevents a duplicate charge."""

    def load_done(self, task_id):
        return set()

    def mark_done(self, task_id, step):
        pass

    def idempotency_key(self, task_id, step):
        return f"{task_id}:{step}"


async def main():
    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()
    try:
        await js.add_stream(name=STREAM, subjects=[SUBJECT])
    except Exception:
        pass  # stream already exists from an earlier run
    sub = await js.pull_subscribe(SUBJECT, durable=DURABLE, config=ConsumerConfig(ack_wait=ACK_WAIT_SECONDS))
    print(f"[worker] connected to {NATS_URL}; waiting for tasks on {SUBJECT}", flush=True)
    while True:
        try:
            msgs = await sub.fetch(1, timeout=5)
        except Exception:
            continue  # no message this round, keep polling
        for msg in msgs:
            task_id = msg.data.decode()
            deliveries = msg.metadata.num_delivered
            print(f"[worker] received '{task_id}' (delivery #{deliveries})", flush=True)
            try:
                agent_task.run(QueueStore(), task_id=task_id)
                await msg.ack()
                print(f"[worker] acked '{task_id}'", flush=True)
            except Exception as exc:
                # Do not ack and do not crash the worker: leave the message unacked so
                # JetStream redelivers it instead of taking the whole worker down.
                print(f"[worker] error on '{task_id}', leaving it for redelivery: {exc}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
