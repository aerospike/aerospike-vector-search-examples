#!/bin/bash -e

mkdir -p ./aerospike-cluster/var/log/aerospike
mkdir -p ./aerospike-cluster/run/aerospike
mkdir -p ./aerospike-cluster/opt/data
mkdir -p ./aerospike-cluster/usr/udf/lua

docker compose -f aerospike-proximus-compose.yaml up -d
