# 🧾 ModelCard Runtime Metadata Extractor (vLLM + Mistral PoC)

This project sets up a local vLLM inference server using the [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model to extract **live runtime metadata** (tokens/sec, latency, request logs, etc.) as part of a broader **ModelCard generation pipeline** for AI supply chain visibility.

---

## ✅ Summary

You are:

- Running a **chat-tuned open-access LLM** (`Mistral-7B-Instruct`) using [`vLLM`](https://github.com/vllm-project/vllm)
- Collecting real inference-time data from the OpenAI-compatible API
- Using this metadata as input for structured, schema-compliant **ModelCards**
- Preparing for OCI-compatible publishing and discovery of model metadata

---

## 🛠️ Prerequisites

This guide assumes:

- You are running **Fedora 40** (or similar bare-metal Linux)
- You have **NVIDIA A100 GPU(s)** with **CUDA drivers installed**
- You have access to **Hugging Face** with a valid token
- You have installed **CUDA Toolkit 12.x** manually from NVIDIA
- You are comfortable with CLI-based dev and GPU troubleshooting

---

## ⚙️ Setup

### 1. Create Python virtual environment

```bash
python3 -m venv ~/vllm-env
source ~/vllm-env/bin/activate
```

### 2. Install vllm with GPU + PyTorch support

```bash
pip install --upgrade pip
pip install "vllm[torch]"
```

### 3. Export Hugging Face token

```bash
export HUGGING_FACE_HUB_TOKEN=your_token_here
```

## Running Mistral with vLLM

```bash
python3 -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --port 8001

```

## Test Inference

```bash
curl http://localhost:8001/v1/chat/completions   -H "Content-Type: application/json"   -d '{
    "model": "mistralai/Mistral-7B-Instruct-v0.2",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 32,
    "temperature": 0.7
  }' | jq


{
  "id": "chatcmpl-bea709c058ba4e4b82b030ef2d43a9db",
  "object": "chat.completion",
  "created": 1747122733,
  "model": "mistralai/Mistral-7B-Instruct-v0.2",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "reasoning_content": null,
        "content": " The capital city of France is Paris. Paris is one of the most famous cities in the world and is known for its iconic landmarks such as the E",
        "tool_calls": []
      },
      "logprobs": null,
      "finish_reason": "length",
      "stop_reason": null
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "total_tokens": 47,
    "completion_tokens": 32,
    "prompt_tokens_details": null
  },
  "prompt_logprobs": null
}
```

## Runtime Metadata Extraction

Install python package 

```bash
git clone https://github.com/husky-parul/model-card-generator.git
cd model-card-generator
pip install -e .
mcg mistralai/Mistral-7B-Instruct-v0.2

Checking local registry for model: mistralai/Mistral-7B-Instruct-v0.2
Checking Hugging Face for model: mistralai/Mistral-7B-Instruct-v0.2
ModelCard written to ./model-cards/mistralai_Mistral-7B-Instruct-v0.2.yaml

```