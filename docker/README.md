# Aerospike Proximus Docker Compose

## Prerequisite
Locate valid `features.conf` in the current directory:

## Installation Aerospike and Proximus Clusters (docker-compose)
```shell
docker compose -f docker-compose.yaml up -d
```
## Installation Aerospike and Proximus Clusters (as separate docker images)
## Create Docker Network
```shell
docker network create svc
```
## Run Aerospike Cluster
```shell
docker run -d \
--name aerospike-cluster \
--network svc \
-p 3000-3003:3000-3003 \
-v ./config:/etc/aerospike aerospike/aerospike-server-enterprise:7.0.0.5 \
--config-file /etc/aerospike/aerospike.conf
```
## Run Proximus Cluster
```shell
docker run -d \
--name aerospike-proximus \
--network svc \
-p 5000:5000 \
-p 5040:5040 \
-v ./config:/etc/aerospike-proximus \
aerospike.jfrog.io/docker/aerospike/aerospike-proximus-private:0.3.1
```


