# Aerospike Vector Search

> [!NOTE]
> Aerospike Vector Search (AVS) is currently in Beta. [Request an invite](https://aerospike.com/lp/aerospike-vector-search-preview-access/).

This is a companion repo for scripts and examples that are helpful to AVS users. See our [full documentation](https://aerospike.com/docs/vector) for details about how AVS works.

## Installation Examples
This repo contains scripts and configuration details for installing AVS. 
For more information about AVS, see our [install documentation](https://aerospike.com/docs/vector/install). This repo contains the following:

**Note**
This repo contains examples that collect basic usage data about the product including network information. You can opt out of this by disabling Prometheus in any of the install instructions. For example, to disable metrics collection through docker compose, remove the prometheus service from the example docker compose file.

* [Kubernetes install script](./kubernetes) - A bash script and configuration details for [Installing on Kubernetes](https://aerospike.com/docs/vector/install/kubernetes).
* [Docker-compose files](./docker) - The `./docker` folder contains a docker-compose file for deploying Aerospike and AVS as containers. Additionally, each example app has a docker-compose file that deploys Aerospike, AVS, and the application itself. 
  

## Example Applications
This repo contains example apps for developing with AVS. Try these apps to gain a basic understanding before you
start developing your own AVS apps.

* [Basic Search](./basic-search/README.md) - A simple application used to showcase the Python client.
* [Quote Search](./quote-semantic-search/) - An application for semantic text search that includes a small dataset of quotes. 
* [Prism Image Search](./prism-image-search/) - An image search demo that can be used to search JPEG images (no sample dataset included).
