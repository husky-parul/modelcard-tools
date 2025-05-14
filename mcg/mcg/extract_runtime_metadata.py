import time
import requests
import uuid

URL =  "http://localhost:8001/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Explain what a ModelCard is."}],
    "max_tokens": 64,
    "temperature": 0.7
}

start = time.time()
response = requests.post(URL, headers=HEADERS, json=payload)
end = time.time()

data = response.json()
usage = data.get("usage", {})
latency = (end - start) * 1000
tokens = usage.get("total_tokens", 0)

print({
    "id": str(uuid.uuid4()),
    "model": MODEL,
    "prompt_tokens": usage.get("prompt_tokens", 0),
    "completion_tokens": usage.get("completion_tokens", 0),
    "total_tokens": tokens,
    "latency_ms": round(latency, 2),
    "tokens_per_sec": round(tokens / (latency / 1000), 2) if latency > 0 else None,
    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
})
