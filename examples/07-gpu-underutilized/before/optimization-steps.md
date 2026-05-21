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

Once the model is warm (steady-state ~200ms), send five requests concurrently:

```bash
for i in $(seq 1 5); do
  curl -s http://localhost:11434/api/generate \
    -d '{"model": "qwen:0.5b", "prompt": "Hello world", "stream": false}' \
    | jq '.total_duration / 1000000 | round' &
done
wait
```

The parallelism signal is the **spread**, not the absolute values. All five results print at roughly the same time and land within ~200ms of each other regardless of count.

If the model just loaded (cold), absolute values will be high but the spread is still tight:

```
16055
16120
16151
16184
16215
```

After the warmup steps above, absolute values drop to steady state:

```
203
215
248
290
312
```

With `server.py`, the same five requests print one at a time, each ~500ms apart — ~2.5s total. Here the entire batch lands within a ~160ms window. That is continuous batching.

### Step 2 — Observe quantization

Pull both the Q4 and FP16 variants of the same model:

```bash
ollama pull llama3.2:3b           # Q4 — already pulled in Step 1
ollama pull llama3.2:3b:fp16      # FP16 — ~6.4 GB
```

Then compare sizes:

```bash
ollama list
```

Expected output:
```
NAME                ID              SIZE      MODIFIED
qwen:0.5b           b5dc5e784f2a    394 MB    ...
llama3.2:3b         a80c4f17acd5    2.0 GB    ...
llama3.2:3b:fp16    c5b4778b90a1    6.4 GB    ...
```

Same model, 3.2× size difference. The Q4 variant fits in 2 GB of HBM; the FP16 variant needs 6.4 GB. At inference time, every token step reads proportionally less memory with Q4 — the GPU finishes each step faster, so throughput improves without changing the model's weights or outputs.

Send an inference request to each and compare latency:

```bash
echo "Q4 (quantized):"
curl -s http://localhost:11434/api/generate \
  -d '{"model": "llama3.2:3b", "prompt": "What is Kubernetes?", "stream": false}' \
  | jq '{total_ms: (.total_duration / 1000000 | round), tokens: .eval_count}'

echo "FP16 (full precision):"
curl -s http://localhost:11434/api/generate \
  -d '{"model": "llama3.2:3b:fp16", "prompt": "What is Kubernetes?", "stream": false}' \
  | jq '{total_ms: (.total_duration / 1000000 | round), tokens: .eval_count}'
```

Expected output (Apple Silicon, will vary by machine):
```
Q4 (quantized):
{ "total_ms": 4100, "tokens": 64 }

FP16 (full precision):
{ "total_ms": 9800, "tokens": 64 }
```

Same token count, roughly 2× the wall time for FP16. The gap widens at longer outputs — every additional token pays the extra memory-read cost again. On a GPU with constrained HBM bandwidth (every GPU), this cost compounds at scale.

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

Expected output:
```
First request (full prefill):
{ "total_ms": 325, "prompt_eval_ms": 108 }

Second request (prefix cached — prompt_eval_ms should be lower):
{ "total_ms": 238, "prompt_eval_ms": 32 }
```

`prompt_eval_ms` is the prefill cost. The second request reuses the cached KV state for the shared prefix — `prompt_eval_ms` drops from 108ms to 32ms, a 3.4× reduction. `total_ms` also falls because less prefill work means the response starts sooner. The longer the shared prefix (system prompts, few-shot examples), the bigger the saving.

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
