# Aerospike Vector Search

> [!NOTE]
> Aerospike Vector Search (AVS) is currently in Beta. [Request an invite](https://aerospike.com/lp/aerospike-vector-search-preview-access/)

This is a companion repo for scripts and examples that are helpful to AVS users. See our [full documentation](https://aerospike.com/docs/vector) for details about how AVS works.

## Installation Examples
This repo contains scripts and configuration for installing AVS. 
For more details on AVS see our [install documentation](https://aerospike.com/docs/vector/operate/install). Here you will find.

* [Kubernetes install script](./kubernetes) - A bash script and configuration for [Installing on Kubernetes](https://aerospike.com/docs/vector/operate/install/kubernetes).
* [Docker-compose files](./docker) - The `./docker` folder contains a docker-compose file for deploying Aerospike, and AVS as containers. Additionaly each example app has a docker-compose file that deploys Aerospike, AVS and the application itself. 
  

## Example Applications
This repo also contains example apps for developing using Aerospike Vector Search. This can give you the basics
to start developing your own AVS application(s).

* [Basic Search](./basic-search/README.md) - A simple application used to showcase the Python client.
* [Quote Search](./quote-semantic-search/) - A application for semantic text search that includes a small dataset of quotes. 
* [Prism Image Search](./prism-image-search/) - An image search demo that can be used to search JPEG images (no sample dataset included).
