# Aerospike Vector Search (AVS) Multi-Node Docker Compose

## Prerequisite
Locate valid `features.conf` in the `./container-volumes/features` directory:

> [!IMPORTANT]
> If you are running MacOS you will need to replace all occurrences of port 5000 with 
> port 5002 in your docker compose file and aerospike-vector-search.yml files.

## Load Balanced 2 Node AVS Cluster
```shell
docker compose -f docker-compose-2-avs-load-balanced.yaml up -d
```

## Plain 2 Node AVS Cluster
```shell
docker compose -f docker-compose-2-avs.yaml up -d
```


