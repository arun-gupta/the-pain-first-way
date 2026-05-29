"""before/: the agent keeps all state in process memory.

A new pod starts with an empty store, so nothing is remembered across a
restart: the task starts over from the top, and because the idempotency key
was never persisted, the retry invents a new one. The sink cannot dedupe it,
so the charge is recorded twice.
"""
import time
import uuid

import agent_task


class MemoryStore:
    def __init__(self):
        self._done = {}

    def load_done(self, task_id):
        # In-process only. A fresh pod starts empty.
        return set(self._done.get(task_id, []))

    def mark_done(self, task_id, step):
        self._done.setdefault(task_id, []).append(step)

    def idempotency_key(self, task_id, step):
        # No durable record of the key, so a retry cannot reuse it.
        return f"{task_id}:{step}:{uuid.uuid4().hex[:8]}"


if __name__ == "__main__":
    agent_task.run(MemoryStore())
    # Idle so the pod stays Running, like a long-lived agent. A Deployment
    # recreates this pod when you delete it, simulating a process restart.
    while True:
        time.sleep(3600)
