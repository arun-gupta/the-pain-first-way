"""after-queue/: a durable queue holds the task and redelivers it on crash (option C).

The worker pulls a task from a NATS JetStream stream, runs it, and acks only on
success. If it crashes before the ack, JetStream redelivers the whole work item to a
new worker after the ack-wait window. There is no per-step checkpoint here: the queue
knows only "acked or not", so the redelivered worker reprocesses every step. The stable
idempotency key is what keeps the charge at exactly one.
"""
import asyncio
import os
import threading

import nats

import agent_task

NATS_URL = os.environ.get("NATS_URL", "nats://nats:4222")
STREAM = "tasks"
SUBJECT = "tasks.run"
DURABLE = "worker"
STEP_DELAY = float(os.environ.get("STEP_DELAY", "5"))
# When set, the worker kills itself partway through its FIRST delivery of a task, a
# deterministic stand-in for a real crash (node failure, OOM kill) so the redelivery
# demo does not depend on winning a race to delete the pod mid-task.
CRASH_FIRST_ATTEMPT = os.environ.get("CRASH_FIRST_ATTEMPT", "").lower() in ("1", "true", "yes")


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
    sub = await js.pull_subscribe(SUBJECT, durable=DURABLE)
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
            if CRASH_FIRST_ATTEMPT and deliveries == 1:
                print("[worker] CRASH_FIRST_ATTEMPT set: this worker will die mid-task before acking", flush=True)
                threading.Timer(STEP_DELAY * 1.5, lambda: os._exit(1)).start()
            agent_task.run(QueueStore(), task_id=task_id)
            await msg.ack()
            print(f"[worker] acked '{task_id}'", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
