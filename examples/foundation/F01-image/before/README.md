# Before: the typical Python-script way

The way most AI/ML developers actually ship things: clone, install, run.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Expected output:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

(On first run, `sentence-transformers` downloads `all-MiniLM-L6-v2` (~22 MB) to `~/.cache/huggingface/` before the server starts. Subsequent starts load from cache.)

In another terminal:

```bash
curl -X POST http://localhost:8000/embed \
  -H 'content-type: application/json' \
  -d '{"text": "hello"}'
```

```json
{"text":"hello","dim":384,"embedding_preview":[0.028,0.123,-0.045,0.056,0.089,-0.012,0.034,0.078]}
```

## What breaks when you ship this to a real machine

You SSH to a Linux VM, `git clone`, `pip install -r requirements.txt`, `python -m uvicorn app:app`. Some of the things that go wrong, in roughly the order you'll discover them:

- **Wrong Python.** The VM has 3.10; your laptop has 3.12. Some wheels match, some don't. `pip install` works; `import` doesn't.
- **Missing system libs.** PyTorch needs `libgomp1` for OpenMP. macOS has the equivalent; minimal Ubuntu images don't. You get `OSError: libgomp.so.1: cannot open shared object file`.
- **The model isn't there.** `sentence-transformers` downloads to `~/.cache/huggingface` on first call. The VM has no cache. The first request takes 30+ seconds, or fails if the VM has no internet.
- **Pip versions drift.** Your `requirements.txt` pins `sentence-transformers==3.2.1`, but that pulls a transitive dependency whose wheel differs between macOS-arm64 and linux-x64.

These are the visible failures. Env vars in your `.zshrc`, HF tokens at `~/.huggingface/token`, hardcoded paths: all leak from the host without you noticing.

## Why isn't a virtualenv enough?

Fair question. Most AI/ML devs use venv (or conda) and find it works for development. Here's where it stops being enough at deployment.

**What a venv solves:**

- Project-level isolation of Python packages on a single machine. Your `transformers==4.41` doesn't collide with another project's `transformers==4.30`.
- Reproducibility within one machine, as long as nothing on the system changes underneath.

**What a venv doesn't touch:**

- **The Python interpreter version.** `python3 -m venv .venv` uses whatever `python3` is on PATH at the moment. Your laptop might have 3.12 from brew; prod might have 3.10 from apt. The venv binds to whatever made it. `requirements.txt` has no Python-version field.
- **Transitive dependencies and wheel platforms.** `pip install` resolves transitives at install time and picks a wheel per (OS, arch, Python version). Same `requirements.txt` produces different binaries on macos-arm64 vs linux-x86_64.
- **System libraries.** PyTorch needs `libgomp1` for OpenMP, `libstdc++` of the right ABI, sometimes `libssl`. These come from the host OS, not from pip.
- **Model weights.** HuggingFace downloads to `~/.cache/huggingface/hub/`, shared across every HF-using project on your user account, entirely outside the venv.
- **Environment variables.** `HF_TOKEN`, `CUDA_HOME`, `LD_LIBRARY_PATH`. Inherited from the parent shell.
- **The GPU stack.** NVIDIA driver, CUDA toolkit, cuDNN. Kernel-level or system-installed. The venv is not in the conversation.

**Conda gets you further** because it manages non-Python deps and pins a Python version per env. But conda envs are still tied to the machine they live on, the channels they were built from, and the system below them. `conda env export` works across identical hosts and breaks across different ones.

**The Dockerfile changes nothing about your dev workflow.** It is not a replacement for venv or conda when you're writing code. It replaces them as the _deployment boundary_. Inside the image, you can still use a venv if you want (some teams do, for layer caching). The image is what crosses machines reliably; the venv is what helps you work on one machine.

The [after/](../after/) folder shows the Dockerfile that draws that boundary.
