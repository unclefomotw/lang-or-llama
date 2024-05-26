#!/usr/bin/env bash
set -o nounset
set -o errexit
set -o pipefail

container_name="qdrant"

if docker inspect "$container_name" > /dev/null 2>&1; then
    if $(docker inspect -f '{{.State.Status}}' "$container_name" | grep -q "running"); then
        echo "The container $container_name is running."
    else
        docker start "$container_name"
    fi
else
    docker run --name "$container_name" -p 6333:6333 -p 6334:6334 \
        --memory 2048m \
        -v $(pwd)/qdrant_storage:/qdrant/storage:z \
        qdrant/qdrant
fi
