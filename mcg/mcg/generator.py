import os
import uuid
import yaml
import time
import requests
from datetime import datetime



import importlib.resources

def get_template_path():
    with importlib.resources.path("mcg.templates", "runtime_template.yaml") as p:
        return str(p)

TEMPLATE_PATH = get_template_path()
MODEL_CARD_DIR = "./model-cards"
VLLM_PORT = 8001  # assumes vLLM server is running here

def check_local_registry(model_name):
    # TODO: check actual OCI registry (registry:2)
    print(f"Checking local registry for model: {model_name}")
    return False  # simulate miss for now

def query_huggingface(model_name):
    print(f"Checking Hugging Face for model: {model_name}")
    response = requests.get(f"https://huggingface.co/api/models/{model_name}")
    return response.status_code == 200

def get_runtime_metadata(model_name):
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "max_tokens": 32,
        "temperature": 0.7
    }

    start = time.time()
    res = requests.post(
        f"http://localhost:{VLLM_PORT}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    end = time.time()

    data = res.json()
    usage = data.get("usage", {})
    latency = (end - start) * 1000
    tokens = usage.get("total_tokens", 0)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "latency_ms": round(latency, 2),
        "tokens_per_sec": round(tokens / (latency / 1000), 2) if latency else None
    }

def generate_modelcard(model_name):
    if not os.path.exists(MODEL_CARD_DIR):
        os.makedirs(MODEL_CARD_DIR)

    if not check_local_registry(model_name):
        if not query_huggingface(model_name):
            print(f"Model '{model_name}' not found in Hugging Face.")
            return

    with open(TEMPLATE_PATH, "r") as f:
        card = yaml.safe_load(f)

    runtime_data = get_runtime_metadata(model_name)
    card["runtime"].update(runtime_data)

    # placeholder for core and evals
    card["core"] = {
        "model_name": model_name,
        "model_id": str(uuid.uuid4()),
        "source": "huggingface"
    }

    card["evals"] = {}  # not populated yet

    out_path = os.path.join(MODEL_CARD_DIR, f"{model_name.replace('/', '_')}.yaml")
    with open(out_path, "w") as f:
        yaml.dump(card, f, sort_keys=False)

    print(f"ModelCard written to {out_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python mcg.py <model_name>")
        exit(1)

    generate_modelcard(sys.argv[1])
