# Pain F.01 example: the same model, two deployments

A working demonstration of [Pain F.01: Model works locally, breaks in prod](../../pains/F01-model-works-locally.md). Same Python code, two deployment styles. The Dockerfile is the only thing that changes. And it changes everything.

## What's here

```
01-image/
├── before/        # the typical Python-script-on-a-VM way
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
└── after/         # the cloud native way
    ├── app.py     # IDENTICAL to before/app.py
    ├── requirements.txt   # IDENTICAL too
    ├── Dockerfile
    ├── .dockerignore
    ├── build.sh
    └── README.md
```

The model: `sentence-transformers/all-MiniLM-L6-v2`. About 22MB. The app exposes `POST /embed`.

## The point of the diff

`before/app.py` and `after/app.py` are byte-for-byte identical. So are `requirements.txt`. **The cloud-native version wraps your code; it doesn't replace it.** The Dockerfile is the entire delta.

## See what your environment actually carries

Before reading the Dockerfile, run this on your laptop. It prints the Python installs, HuggingFace cache, and relevant environment variables currently on your system. Whatever it shows is what your `before/` deployment quietly depends on.

```bash
echo "=== Pythons on PATH ==="; which -a python python3 2>/dev/null | sort -u
echo "=== Active Python ==="; python3 -c "import sys; print(sys.executable, sys.version.split()[0])"
echo "=== HuggingFace cache ==="; du -sh "${HF_HOME:-$HOME/.cache/huggingface}" 2>/dev/null || echo "(no cache yet)"
echo "=== Relevant env vars ==="; env | grep -E '^(CUDA|HF_|TRANSFORMERS_|TORCH_|LD_LIBRARY)' | sort
```

Common things this surfaces: multiple Python installs (the "active" one is often not the one your editor uses), a multi-gigabyte HuggingFace cache shared across projects, and env vars baked into your shell that won't exist on a prod VM. None of this is captured by `git push`. The Dockerfile is one way to make it explicit.

## Run the two versions

Both serve at `localhost:8000/embed`. Same curl, same response. The difference is everything around the response.

- [`before/README.md`](before/README.md) — run instructions and the failure modes the typical approach hits on a real Linux VM
- [`after/README.md`](after/README.md) — run instructions and what the Dockerfile actually declares

## Trade-offs

**What you keep**: your `app.py`, your `requirements.txt`, your model artifacts. All unchanged.

**What you give up**: "it works on my machine" as a defense. The image either runs everywhere or runs nowhere.

---

[← Back to Pain F.01](../../pains/F01-model-works-locally.md) · [Landscape](../../README.md) · [Examples index](../README.md)
