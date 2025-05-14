# Scenario: Multi-Registry ModelCard Discovery Setup

- Two local registries: localhost:8080 and localhost:5001
- One push.sh script to upload models + modelcards
- One unified pull_index.py to discover across both registries
- One shared modelcard.db

## Steps

- Push model + modelcard to a different regitsry.
- Attach modelcard to model

```
mkdir -p services/oci-artifacts/falcon
echo "# Falcon model file" > services/oci-artifacts/falcon/model-falcon.txt

cat > services/oci-artifacts/falcon/modelcard-falcon.json <<EOF
{
  "hash": "sha256:falconabc123",
  "model_name": "falcon-7b",
  "f1_score": 0.83,
  "license": "apache-2.0",
  "dataset": "pile",
  "cve_count": 2
}
EOF

podman run -d --name registry1 -p 5001:5001 -v ./registry-data:/var/lib/registry -v ./registry-config.yaml:/etc/docker/registry/config.yml:ro,Z registry:2

REGISTRY=localhost:5001 REPO_PREFIX=modelcard-alt ./push.sh oci-artifacts/falcon

```

- Index modelcards

```
python pull_index.py
🔍 Crawling localhost:8080/modelcard-demo
📎 localhost:8080/modelcard-demo/bert:v1 -> 1 modelcard(s): ['sha256:c6cdbb70f61a3c119ebe084606637068a56745ca2e2c5881750b77514efdf9f5']
⚠  Already in DB: sha256:bert456def
✅ Indexed modelcard for localhost:8080/modelcard-demo/bert:v1 @ sha256:c6cdbb70f61a3c119ebe084606637068a56745ca2e2c5881750b77514efdf9f5
📎 localhost:8080/modelcard-demo/llama:v1 -> 1 modelcard(s): ['sha256:af110d2d72fa3b7a106052edc247aa19e37c977f9ebcd9c65b124fe1c8a1d94e']
⚠  Already in DB: sha256:llama2abc123
✅ Indexed modelcard for localhost:8080/modelcard-demo/llama:v1 @ sha256:af110d2d72fa3b7a106052edc247aa19e37c977f9ebcd9c65b124fe1c8a1d94e
📎 localhost:8080/modelcard-demo/mistral:v1 -> 1 modelcard(s): ['sha256:1d1c5ade1f0bd9b42e5347214bb9edff53ff372d5791986e0c6fa8efbb9d6634']
⚠  Already in DB: sha256:mistral789ghi
✅ Indexed modelcard for localhost:8080/modelcard-demo/mistral:v1 @ sha256:1d1c5ade1f0bd9b42e5347214bb9edff53ff372d5791986e0c6fa8efbb9d6634
🔍 Crawling localhost:5001/modelcard-alt
📎 localhost:5001/modelcard-alt/falcon:v1 -> 1 modelcard(s): ['sha256:84e762aea87ee73efeaa642aa858dd5b2348799d3ed0f41e2cb85581af5faa96']
⚠  Already in DB: sha256:falconabc123
✅ Indexed modelcard for localhost:5001/modelcard-alt/falcon:v1 @ sha256:84e762aea87ee73efeaa642aa858dd5b2348799d3ed0f41e2cb85581af5faa96
```

- Search

```
cd services/search

uvicorn search_service:app --reload --port 8000

```

```
curl "http://localhost:8000/search?model_name=falcon-7b" | jq

[
  {
    "hash": "sha256:falconabc123",
    "model_name": "falcon-7b",
    "f1_score": 0.83,
    "license": "apache-2.0",
    "dataset": "pile",
    "cve_count": 2
  }
]
```

```
curl "http://localhost:8000/search?f1_score_gte=0.80" | jq

[
  {
    "hash": "sha256:llama2abc123",
    "model_name": "llama-2-7b",
    "f1_score": 0.87,
    "license": "apache-2.0",
    "dataset": "c4",
    "cve_count": 0
  },
  {
    "hash": "sha256:mistral789ghi",
    "model_name": "mistral-7b-instruct",
    "f1_score": 0.91,
    "license": "mit",
    "dataset": "refinedweb",
    "cve_count": 0
  },
  {
    "hash": "sha256:falconabc123",
    "model_name": "falcon-7b",
    "f1_score": 0.83,
    "license": "apache-2.0",
    "dataset": "pile",
    "cve_count": 2
  }
]
```
