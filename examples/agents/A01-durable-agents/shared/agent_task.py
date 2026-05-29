"""The agent's task, identical in every variant: reserve -> charge -> email
-> confirm. Each step has a side effect sent to the sink.

This module is mechanism-agnostic. Durability comes entirely from the `store`
that each variant's main.py passes to run():
  - load_done(task_id)              which steps are already finished
  - mark_done(task_id, step)        record a step as finished
  - idempotency_key(task_id, step)  the key sent with the step's side effect

The crash window is the sleep between sending a step's side effect and
recording it as done. Killing the pod there is what separates a durable store
(resumes, no duplicate charge) from an in-memory one (restarts, duplicates).
"""
import json
import os
import time
import urllib.request

STEPS = ["reserve", "charge", "email", "confirm"]
SINK_URL = os.environ.get("SINK_URL", "http://sink")
TASK_ID = os.environ.get("TASK_ID", "user-task-1")
STEP_DELAY = float(os.environ.get("STEP_DELAY", "5"))


def _send_effect(step, key):
    body = json.dumps({"type": step, "key": key}).encode()
    req = urllib.request.Request(
        f"{SINK_URL}/effect",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())["status"]


def run(store):
    done = store.load_done(TASK_ID)
    print(f"[agent] task {TASK_ID}: resuming, already done = {sorted(done) or 'nothing'}", flush=True)
    for step in STEPS:
        if step in done:
            print(f"[agent]   {step}: skip (already done)", flush=True)
            continue
        key = store.idempotency_key(TASK_ID, step)
        status = _send_effect(step, key)
        print(f"[agent]   {step}: side effect sent (key={key}) -> sink: {status}", flush=True)
        time.sleep(STEP_DELAY)  # <-- crash window: kill the pod here
        store.mark_done(TASK_ID, step)
        print(f"[agent]   {step}: recorded done", flush=True)
    print(f"[agent] task {TASK_ID}: complete", flush=True)
