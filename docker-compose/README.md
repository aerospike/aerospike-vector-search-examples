# Aerospike Proximus Docker Compose

## Prerequisite
Locate valid `features.conf` in the following directories:
* `./aerospike-cluster/etc/aerospike`
* `./aerospike-proximus/etc/aerospike-proximus`

## Installation Aerospike and Proximus Clusters
```shell
./install.sh
```
## To Start Prism Image Search Run:
```shell
cd "$(git rev-parse --show-toplevel)/prism-image-search" && docker build -f "Dockerfile-prism" -t "prism" . && cd -

docker run -d \
--name "prism-image-search" \
-v "$(git rev-parse --show-toplevel)/prism-image-search/container-volumes/prism/images:/prism/static/images/data" \
--network "svc" -p "8080:8080" -e "PROXIMUS_HOST=aerospike-proximus" -e "PROXIMUS_PORT=5000" prism
```
## To Start Quote Semantic Search Run:
```shell
cd "$(git rev-parse --show-toplevel)/quote-semantic-search" && docker build -f "Dockerfile-quote-search" -t "quote-search" . && cd -

docker run -d \
--name "quote-search" \
-v "$(git rev-parse --show-toplevel)/quote-semantic-search/container-volumes/quote-search/data:/container-volumes/quote-search/data" \
--network "svc" -p "8080:8080" \
-e "PROXIMUS_HOST=aerospike-proximus" \
-e "PROXIMUS_PORT=5000" \
-e "APP_NUM_QUOTES=5000" \
-e "GRPC_DNS_RESOLVER=native" quote-search
```

## Uninstall Clusters


