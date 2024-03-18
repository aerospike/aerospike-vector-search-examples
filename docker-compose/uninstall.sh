#!/bin/bash -e

rm -rf ./aerospike-cluster/var
rm -rf ./aerospike-cluster/run
rm -rf ./aerospike-cluster/opt
rm -rf ./aerospike-cluster/usr

remove_container() {
  CONTAINER_ID="$(docker ps -aq -f name="$1")"
  if [ ! -z "$CONTAINER_ID" ]; then
     docker stop "$CONTAINER_ID"
     docker rm "$CONTAINER_ID"
  fi
}

remove_container "quote-search"
remove_container "prism-image-search"

docker compose -f aerospike-proximus-compose.yaml down
