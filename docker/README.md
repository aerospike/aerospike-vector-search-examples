# Aerospike Vector Search (AVS) Docker Compose

## Prerequisite
Locate valid `features.conf` in the `./config` directory:

> [!IMPORTANT]
> If you are running MacOS you will need to replace all occurances of port 5000 with 
> port 5002 in your docker compose file and aerospike-proximus.yml file.

## Installation Aerospike and AVS Clusters (docker-compose)
```shell
docker compose -f docker-compose.yaml up -d
```
## Installation Aerospike and AVS Clusters (as separate docker images)
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
## Run AVS Cluster
```shell
docker run -d \
--name aerospike-vs \
--network svc \
-p 5000:5000 \
-p 5040:5040 \
-v ./config:/etc/aerospike-proximus \
aerospike/aerospike-proximus:0.4.0
```


