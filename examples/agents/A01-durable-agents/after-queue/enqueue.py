"""Publish one task onto the queue, or purge the stream. Run inside the worker pod,
which already has the nats client installed:
  kubectl exec deploy/payments-agent -- python /app/enqueue.py          # publish one task
  kubectl exec deploy/payments-agent -- python /app/enqueue.py purge    # clear the stream
"""
import asyncio
import os
import sys

import nats

NATS_URL = os.environ.get("NATS_URL", "nats://nats:4222")
STREAM = "tasks"
SUBJECT = "tasks.run"
TASK_ID = os.environ.get("TASK_ID", "user-task-1")


async def main():
    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()
    if "purge" in sys.argv[1:]:
        await js.purge_stream(STREAM)
        print(f"[enqueue] purged stream '{STREAM}'")
    else:
        ack = await js.publish(SUBJECT, TASK_ID.encode())
        print(f"[enqueue] published '{TASK_ID}' (stream seq {ack.seq})")
    await nc.close()


if __name__ == "__main__":
    asyncio.run(main())
