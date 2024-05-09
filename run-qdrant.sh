#!/usr/bin/env bash
set -o nounset
set -o errexit
set -o pipefail

docker run -p 6333:6333 -p 6334:6334 \
    --memory 2048m \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
