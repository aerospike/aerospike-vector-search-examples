# Aerospike Vector Search (AVS) Docker Compose

## Prerequisite
Locate valid `features.conf` in the `./config` directory:

## Installation Aerospike and AVS Clusters (docker-compose)
```shell
docker compose -f docker-compose.yaml up -d
```
To run AVS using Aerospike 6.4 server
```shell
docker compose -f docker-compose-asdb-6.4.yml up -d
```
## Installation Aerospike and AVS Clusters (as separate docker images)
## Create Docker Network
```shell
docker network create svc
```
## Run Aerospike Cluster

### Using Aerospike 7.0
```shell
docker run -d \
--name aerospike-cluster \
--network svc \
-p 3000-3003:3000-3003 \
-v ./config:/etc/aerospike aerospike/aerospike-server-enterprise:7.0.0.5 \
--config-file /etc/aerospike/aerospike.conf
```
### Using Aerospike 6.4 
```shell
docker run -d \
--name aerospike-cluster \
--network svc \
-p 3000-3003:3000-3003 \
-v ./config:/etc/aerospike aerospike/aerospike-server-enterprise:6.4.0.26 \
--config-file /etc/aerospike/aerospike-6.4.conf
```

## Run AVS Cluster
```shell
docker run -d \
--name aerospike-vs \
--network svc \
-p 5555:5000 \
-p 5040:5040 \
-v ./config:/etc/aerospike-vector-search \
aerospike/aerospike-vector-search:1.0.0
```


