# Scenario: Cross-Registry discovery

-  Model in Registry A (e.g. localhost:8080)
-  ModelCard in Registry B (e.g. localhost:5001)

>Note: OCI does not support cross-registry referrers. oras attach will not link artifacts across registries.

## Demo Objecives

- Push model to Registry A (localhost:8080)

- Push modelcard to Registry B (localhost:5001)

- During discovery, infer link based on naming or metadata (e.g. shared hash or model name)

## Steps

- create artifacts

```
mkdir -p services/oci-artifacts/xgen

echo "# Dummy XGen model file" > services/oci-artifacts/xgen/model-xgen.txt

cat > services/oci-artifacts/xgen/modelcard-xgen.json <<EOF
{
  "hash": "sha256:xgen789abc",
  "model_name": "xgen-7b",
  "f1_score": 0.82,
  "license": "apache-2.0",
  "dataset": "openwebtext",
  "cve_count": 1
}
EOF

tree services/oci-artifacts/xgen/services/oci-artifacts/xgen/
├── modelcard-xgen.json
└── model-xgen.txt

```

- Push model to Registry A (localhost:8080)

```
REGISTRY=localhost:8080 ./push.sh services/oci-artifacts/xgen --only-model
```

- Push modelcard to Registry B (localhost:5001)

```
REGISTRY=localhost:8080 services/push.sh services/oci-artifacts/xgen --only-model

📤 Pushing model to: localhost:8080/modelcard-demo/xgen:v1
✓ Exists    services/oci-artifacts/xgen/model-xgen.txt                            24/24  B 100.00%     0s
  └─ sha256:e9115f7a51407352fa55cd8b7d76d18230f441aafede12f2c8e4f0921a655cae
✓ Exists    application/vnd.oci.empty.v1+json                                       2/2  B 100.00%     0s
  └─ sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
✓ Uploaded  application/vnd.oci.image.manifest.v1+json                          610/610  B 100.00%     0s
  └─ sha256:188d9deb6c5e0e6541e59608f2d2191c0d0d663df434789fd0aff009c25567a1
Pushed [registry] localhost:8080/modelcard-demo/xgen:v1
ArtifactType: application/octet-stream
Digest: sha256:188d9deb6c5e0e6541e59608f2d2191c0d0d663df434789fd0aff009c25567a1
✅ Done: xgen

```

- Push modelcard as a freestanding artifact

```
 oras push --plain-http localhost:5001/modelcard-xgen:card \
  --artifact-type application/vnd.oci.modelcard.v1+json \
  services/oci-artifacts/xgen/modelcard-xgen.json
✓ Uploaded  services/oci-artifacts/xgen/modelcard-xgen.json                     154/154  B 100.00%   18ms
  └─ sha256:f7d3ef8276ba909909fcd75ce91e4f05ee2e74b86ddea9fb60360bc8aa8fa0e4
✓ Uploaded  application/vnd.oci.empty.v1+json                                       2/2  B 100.00%   14ms
  └─ sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
✓ Uploaded  application/vnd.oci.image.manifest.v1+json                          629/629  B 100.00%     0s
  └─ sha256:481e09818ad270cd5ae37d63682c647e3a0bdc13cba5d6126db2170497b6e986
Pushed [registry] localhost:5001/modelcard-xgen:card
ArtifactType: application/vnd.oci.modelcard.v1+json
Digest: sha256:481e09818ad270cd5ae37d63682c647e3a0bdc13cba5d6126db2170497b6e986

```