# Aerospike Vector Search (Proximus)

> [!NOTE]
> Aerospike Vector Search (AVS) is currently in Alpha and available by invitation only. Breaking changes to our client and APIs are expected. Please refer to our [documentation](https://aerospike-vector-search.netlify.app/vector/) for more details and to request access.


## Sample Applications
This repo contains sample apps for utilizing Aerospike Vector Search. All of the current 
apps are written in Python. The available apps are:

* [Basic Search](./basic-search/README.md) - A simple application used to showcase the Python client.
* [Quote Search](./quote-semantic-search/) - This is a semantic text search that includes a small dataset of quotes. 
* [Prism Image Search](./prism-image-search/) - This is an image search demo that can be used to search jpgs. (No dataset included in this example. )

## Prerequisites
You don't have to know Aerospike to get started, but you do need the following:

1. A Python 3.10 - 3.11 environment and familiarity with the Python programming language (see [Setup Python Virtual Environment](./prism-image-search/README.md#setup-python-virtual-environment)).
1. The URL to your private sandbox environment (this will be provided).

## Development
To development you can run AVS using [docker](./docker/README.md) and each of the sample application
contains a docker-compose file that deploys all the necessary components. 

# Contributing
If you have an idea for a sample application, open a PR and we will review it. We're excited to provide more examples of what Vector Search can do.
