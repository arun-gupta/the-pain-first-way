# Pre-CN optimizations: the AI/ML developer path

Before reaching for Kubernetes, AI/ML developers optimize at the model and serving engine layer. Each step below builds on the previous one. Steps 1–3 are fully runnable on a Mac without a GPU.

## Prerequisites

vLLM requires Python 3.9–3.12. Python 3.13 is not yet supported. Check your version:

```bash
python3 --version
```

If you are on 3.13, install 3.12 via Homebrew and use it explicitly:

```bash
brew install python@3.12
```

Create a virtual environment and install vLLM:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install vllm
```

## Step 0 — The problem (already seen in server.py)

`server.py` processes one request at a time. Five concurrent requests take ~2.5s. The GPU idles between them.

## Step 1 — Switch to vLLM (continuous batching, the biggest win)

Replace the naive serving loop with vLLM. Continuous batching is on by default — no flags needed.

```bash
vllm serve facebook/opt-125m --device cpu
```

`facebook/opt-125m` is ~250 MB, publicly available, no HuggingFace token required, runs on CPU.

Test it:

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "facebook/opt-125m", "prompt": "The GPU utilization is", "max_tokens": 20}'
```

Send five requests concurrently and observe they are processed in parallel rather than sequentially:

```bash
for i in $(seq 1 5); do
  curl -s http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "facebook/opt-125m", "prompt": "The GPU utilization is", "max_tokens": 10}' &
done
wait
```

Check the metrics endpoint vLLM exposes by default:

```bash
curl http://localhost:8000/metrics | grep -E "num_requests_running|gpu_cache_usage"
```

## Step 2 — Enable prefix caching

Avoid recomputing attention for repeated prefixes — system prompts, few-shot examples, shared context.

```bash
vllm serve facebook/opt-125m --device cpu --enable-prefix-caching
```

Send the same prompt twice and observe the second request is faster (cache hit):

```bash
# First request — full prefill cost
time curl -s http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "facebook/opt-125m", "prompt": "You are a helpful assistant. The weather today is", "max_tokens": 20}'

# Second request — prefix cached, prefill skipped
time curl -s http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "facebook/opt-125m", "prompt": "You are a helpful assistant. The capital of France is", "max_tokens": 20}'
```

The shared prefix `"You are a helpful assistant."` is cached after the first request. The second request skips its prefill.

## Step 3 — Enable sequence packing (chunked prefill)

Bin-pack multiple short prompts into one context window to eliminate padding waste.

```bash
vllm serve facebook/opt-125m --device cpu --enable-prefix-caching --enable-chunked-prefill
```

With chunked prefill enabled, vLLM fills each batch step to the token budget rather than leaving gaps at the end of short sequences. Observable as higher `gpu_cache_usage` at the same request rate.

## Step 4 — Quantization (GPU required)

Reduces model weight size and HBM bandwidth per token step. Requires a pre-quantized model and a GPU.

```bash
# AWQ — INT4, requires pre-quantized model variant
vllm serve meta-llama/Llama-3.1-8B-Instruct-AWQ --quantization awq

# FP8 — on H100/A100
vllm serve meta-llama/Llama-3.1-8B-Instruct --quantization fp8
```

A 70B FP16 model at ~140 GB becomes ~35 GB in INT4 — 4× less HBM, proportionally faster memory reads per token step.

## Step 5 — Speculative decoding (GPU required)

A small draft model proposes N tokens; the large model verifies them in one forward pass. Reduces full model reads per output token.

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-model meta-llama/Llama-3.2-1B \
  --num-speculative-tokens 5
```

## Step 6 — Prefill/decode disaggregation (GPU required)

Routes the compute-bound prefill phase and the memory-bandwidth-bound decode phase to separate instances.

```bash
# Prefill instance
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --kv-transfer-config '{"kv_connector":"PyNcclConnector","kv_role":"kv_producer"}'

# Decode instance
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --kv-transfer-config '{"kv_connector":"PyNcclConnector","kv_role":"kv_consumer"}'
```

---

Steps 1–3 improve utilization at the serving engine layer with no infrastructure change. When traffic grows beyond what a single server can handle, the [`after/`](../after/) examples take over: KEDA autoscaling on `inference_requests_in_flight` (Step 2) and GPU partitioning via the GPU Operator (Step 3).
