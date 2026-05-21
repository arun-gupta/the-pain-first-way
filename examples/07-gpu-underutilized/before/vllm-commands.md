# Pre-CN optimizations: vLLM serving commands

These are the model and serving engine optimizations that ML practitioners apply before reaching for Kubernetes. Each is a launch flag or configuration change — no infrastructure required.

## Continuous batching

Replace the naive serving loop (`server.py`) with vLLM. Continuous batching is on by default:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct
```

Typical result: GPU utilization moves from ~30% to ~70–80% at the same traffic level, before any infrastructure change.

## Quantization

Reduce model weight size and HBM bandwidth consumption per token step:

```bash
# AWQ (Activation-aware Weight Quantization) — INT4, requires pre-quantized model
vllm serve meta-llama/Llama-3.1-8B-Instruct-AWQ --quantization awq

# GPTQ — INT4/INT8
vllm serve meta-llama/Llama-3.1-8B-Instruct-GPTQ --quantization gptq

# FP8 — on H100/A100, handled by the engine
vllm serve meta-llama/Llama-3.1-8B-Instruct --quantization fp8
```

A 70B FP16 model at ~140 GB becomes ~35 GB in INT4. Same model, 4× less HBM, faster memory reads per token step.

## KV cache: prefix caching

Avoid recomputing attention for repeated prefixes (system prompts, few-shot examples):

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-prefix-caching
```

Requests that share a common prefix (e.g. the same system prompt) reuse the cached KV state. The first request pays the full prefill cost; subsequent ones skip it.

## Sequence packing (chunked prefill)

Bin-pack multiple short sequences into one context window to eliminate padding waste:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-chunked-prefill
```

Short prompts that would otherwise each occupy a full batch slot are packed together. Fewer batch steps for the same number of requests.

## Speculative decoding

Use a small draft model to propose tokens; the large model verifies them in one forward pass:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-model meta-llama/Llama-3.2-1B \
  --num-speculative-tokens 5
```

Each verification step accepts multiple tokens at once if the draft was correct. Reduces full model reads per output token at the cost of occasional wasted draft work.

## Prefill/decode disaggregation

Route the compute-bound prefill phase and the memory-bandwidth-bound decode phase to separate instances:

```bash
# Prefill instance (handles prompt processing)
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --pipeline-parallel-size 1 \
  --kv-transfer-config '{"kv_connector":"PyNcclConnector","kv_role":"kv_producer"}'

# Decode instance (handles token generation)
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --pipeline-parallel-size 1 \
  --kv-transfer-config '{"kv_connector":"PyNcclConnector","kv_role":"kv_consumer"}'
```

Prefill is compute-bound (large prompt, one pass); decode is memory-bandwidth-bound (one token at a time, many passes). Mixing them on one GPU underserves both. Disaggregation lets each phase run on hardware sized for its profile.

---

Once these are in place, the remaining problems are infrastructure: autoscaling on the right signal and sharing the GPU across workloads. That is where the `after/` examples take over.
