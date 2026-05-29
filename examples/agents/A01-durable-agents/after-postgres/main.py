"""after-postgres/: step state lives in Postgres (option B).

A restart reloads the completed steps and resumes from where it stopped,
skipping work already done. The idempotency key is derived from the durable
task id, so even if the crash lands in the narrow window after a side effect
but before it is recorded done, the retry reuses the same key and the sink
deduplicates it. Either way the charge is recorded exactly once.
"""
import os
import time

import pg8000.native

import agent_task


class PostgresStore:
    def __init__(self):
        self.conn = pg8000.native.Connection(
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", "agentpw"),
            host=os.environ.get("PGHOST", "postgres"),
            database=os.environ.get("PGDATABASE", "agent"),
        )
        self.conn.run(
            "CREATE TABLE IF NOT EXISTS done_steps "
            "(task_id text, step text, PRIMARY KEY (task_id, step))"
        )

    def load_done(self, task_id):
        rows = self.conn.run(
            "SELECT step FROM done_steps WHERE task_id = :t", t=task_id
        )
        return {r[0] for r in rows}

    def mark_done(self, task_id, step):
        # ON CONFLICT makes recording idempotent too: re-marking is a no-op.
        self.conn.run(
            "INSERT INTO done_steps (task_id, step) VALUES (:t, :s) "
            "ON CONFLICT DO NOTHING",
            t=task_id, s=step,
        )

    def idempotency_key(self, task_id, step):
        # Stable: derived from durable state, so a retry reuses it.
        return f"{task_id}:{step}"


if __name__ == "__main__":
    agent_task.run(PostgresStore())
    while True:
        time.sleep(3600)
