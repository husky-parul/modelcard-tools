#!/bin/bash
set -e

# Usage: REGISTRY=<host> ./push.sh <model-dir> [--only-model|--only-card]

if [ -z "$1" ]; then
  echo "Usage: REGISTRY=<host> ./push.sh <model-dir> [--only-model|--only-card]"
  exit 1
fi

MODEL_DIR="$1"
FLAG="$2"

REGISTRY="${REGISTRY:-localhost:8080}"
REPO_PREFIX="${REPO_PREFIX:-modelcard-demo}"
MEDIA_TYPE="application/vnd.oci.modelcard.v1+json"

MODEL_NAME=$(basename "$MODEL_DIR")
MODEL_FILE=$(find "$MODEL_DIR" -name "model-*.txt" | head -n1)
MODELCARD_FILE=$(find "$MODEL_DIR" -name "modelcard-*.json" | head -n1)

FULL_REF="$REGISTRY/$REPO_PREFIX/$MODEL_NAME:v1"

# Push model
if [[ "$FLAG" != "--only-card" ]]; then
  if [ -n "$MODEL_FILE" ]; then
    echo "📤 Pushing model to: $FULL_REF"
    oras push --plain-http "$FULL_REF" \
      --artifact-type application/octet-stream \
      "$MODEL_FILE"
  else
    echo "⚠️  Skipping model push: model file not found."
  fi
fi

# Attach modelcard
if [[ "$FLAG" != "--only-model" ]]; then
  if [ -n "$MODELCARD_FILE" ]; then
    echo "📎 Attaching modelcard: $MODELCARD_FILE"
    oras attach --plain-http "$FULL_REF" \
      --artifact-type "$MEDIA_TYPE" \
      --annotation "org.opencontainers.ref.name=$(basename $MODELCARD_FILE)" \
      "$MODELCARD_FILE"
  else
    echo "⚠️  Skipping modelcard attach: modelcard file not found."
  fi
fi

echo "✅ Done: $MODEL_NAME"
