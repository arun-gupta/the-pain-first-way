# Pre-CN optimizations: the AI/ML developer path

Before reaching for Kubernetes, AI/ML developers optimize at the model and serving engine layer. Two tracks: **Mac (ollama)** for running today without a GPU, and **GPU (vLLM)** for the production path.

---

## Mac path — ollama (no GPU required)

ollama runs natively on Apple Silicon via Metal. All ollama models are GGUF — quantized INT4/INT8 by default, so quantization is built-in from the start.

These steps use **two terminals**. Terminal 1 runs the ollama server; Terminal 2 sends requests.

### Prerequisites

```bash
brew install ollama
brew install jq   # for readable output
```

### Step 0 — The problem (already seen in server.py)

`server.py` processes one request at a time. Five concurrent requests take ~2.5s. The GPU idles between them.

### Step 1 — Switch to ollama (continuous batching)

**Terminal 1** — start the server and leave it running:

```bash
ollama serve
```

**Terminal 2** — pull a small model and send requests:

```bash
ollama pull qwen:0.5b
```

`qwen:0.5b` is ~394 MB, GGUF Q4, no authentication required.

Send the same request three times to observe the model warming up:

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model": "qwen:0.5b", "prompt": "The GPU utilization is", "stream": false}' \
  | jq '{response: .response, total_ms: (.total_duration / 1000000 | round)}'
```

Run it three times. The first request loads the model into memory; subsequent ones hit steady-state:

```
# First request — model loading
{ "response": "...", "total_ms": 918 }

# Second request — warming up
{ "response": "...", "total_ms": 310 }

# Third request — steady state
{ "response": "...", "total_ms": 198 }
```

Once `total_ms` stabilises around 200ms the model is warm. Proceed to the concurrent request demo.

Now send five requests concurrently. All five should complete within ~350ms of each other — contrast with `server.py` where they serialized one at a time and took ~2.5s total:

```bash
for i in $(seq 1 5); do
  curl -s http://localhost:11434/api/generate \
    -d '{"model": "qwen:0.5b", "prompt": "Hello world", "stream": false}' \
    | jq '.total_duration / 1000000 | round' &
done
wait
```

Expected output — all five durations appear at roughly the same time, each ~200ms:
```
203
215
248
290
312
```

### Step 2 — Observe quantization (already applied)

ollama models are GGUF — quantized at pull time. Check what you have:

```bash
ollama list
```

Expected output:
```
NAME         ID            SIZE    MODIFIED
qwen:0.5b    ...           394 MB  ...
```

On a larger model the difference is dramatic: a 7B FP16 model is ~14 GB; the GGUF Q4 variant is ~4 GB. Same model, 3.5× less memory, proportionally faster reads per token step.

### Step 3 — Prefix caching

ollama caches the KV state of repeated prompt prefixes automatically. Send two requests that share a long prefix and observe the second is faster:

```bash
SHARED_PREFIX="You are a helpful assistant that answers questions about cloud native infrastructure."

echo "First request (full prefill):"
curl -s http://localhost:11434/api/generate \
  -d "{\"model\": \"qwen:0.5b\", \"prompt\": \"${SHARED_PREFIX} What is Kubernetes?\", \"stream\": false}" \
  | jq '{total_ms: (.total_duration / 1000000 | round), prompt_eval_ms: (.prompt_eval_duration / 1000000 | round)}'

echo "Second request (prefix cached — prompt_eval_ms should be lower):"
curl -s http://localhost:11434/api/generate \
  -d "{\"model\": \"qwen:0.5b\", \"prompt\": \"${SHARED_PREFIX} What is a pod?\", \"stream\": false}" \
  | jq '{total_ms: (.total_duration / 1000000 | round), prompt_eval_ms: (.prompt_eval_duration / 1000000 | round)}'
```

`prompt_eval_ms` is the prefill cost. The second request reuses the cached KV state for the shared prefix — its `prompt_eval_ms` should be noticeably lower than the first.

---

## GPU path — vLLM (CUDA required)

vLLM requires Linux with a CUDA GPU. The commands below are the production reference.

### Prerequisites

vLLM requires Python 3.9–3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install vllm
```

### Step 1 — Switch to vLLM (continuous batching)

```bash
vllm serve facebook/opt-125m
```

Check the metrics endpoint vLLM exposes by default:

```bash
curl http://localhost:8000/metrics | grep -E "num_requests_running|gpu_cache_usage"
```

### Step 2 — Enable prefix caching

```bash
vllm serve facebook/opt-125m --enable-prefix-caching
```

### Step 3 — Enable sequence packing (chunked prefill)

```bash
vllm serve facebook/opt-125m --enable-prefix-caching --enable-chunked-prefill
```

### Step 4 — Quantization

```bash
# AWQ — INT4
vllm serve meta-llama/Llama-3.1-8B-Instruct-AWQ --quantization awq

# FP8 — H100/A100
vllm serve meta-llama/Llama-3.1-8B-Instruct --quantization fp8
```

### Step 5 — Speculative decoding

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-model meta-llama/Llama-3.2-1B \
  --num-speculative-tokens 5
```

### Step 6 — Prefill/decode disaggregation

```bash
# Prefill instance
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --kv-transfer-config '{"kv_connector":"PyNcclConnector","kv_role":"kv_producer"}'

# Decode instance
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --kv-transfer-config '{"kv_connector":"PyNcclConnector","kv_role":"kv_consumer"}'
```

---

Once serving-engine optimizations are in place, the [`after/`](../after/) examples cover the infrastructure layer: KEDA autoscaling on `inference_requests_in_flight` (Step 2) and GPU partitioning via the GPU Operator (Step 3).
