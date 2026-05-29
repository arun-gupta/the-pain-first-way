# Before: the naive way

Run `python train.py` directly. No checkpointing. Kill it and you lose everything.

## Run it

No dependencies beyond the standard library.

```bash
python3 train.py
```

You'll see 20 epochs printing every 3 seconds:

```
Starting training from epoch 0 (no checkpoint support)
epoch   0/20  loss=2.3000
epoch   1/20  loss=1.8769
epoch   2/20  loss=1.5378
...
```

## Simulate a crash

While it's running, open another terminal and kill it:

```bash
kill $(pgrep -f train.py)
```

Restart it:

```bash
python3 train.py
```

It starts from **epoch 0** again. Every epoch you had completed is gone.

## What this costs in the real world

On a real GPU job:
- Each epoch might take 30--60 minutes on an A100.
- A 14-hour run = epochs 0--13 completed, 14 in progress.
- One preemption, OOM kill, spot-instance reclaim, or network hiccup and you restart from epoch 0.
- 14 hours of GPU time, billed and lost.

The cloud native answer: declare the job to a platform that owns retrying it, and have your code write checkpoints so a restart doesn't mean starting over.

The [after/](../after/) folder shows both pieces.
