# Basic vector search example

A simple Python application that demonstrates vector ANN index creation, 
vector record insertion, and basic ANN query against the AVS server using the Python client.

## Prerequisites

1. A Python 3.10 - 3.11 environment and familiarity with the Python programming language (see [Setup Python Virtual Environment](../prism-image-search/README.md#setup-python-virtual-environment)).
1. An Aerospike Vector Search host (sandbox or local).

## Setup build Python Virtual Environment

This is the recommended mode for building the python client.

```shell
# Create virtual environment to isolate dependencies.
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```shell
python3 -m pip install -r requirements.txt --extra-index-url https://aerospike.jfrog.io/artifactory/api/pypi/aerospike-pypi-dev/simple 
```

```

## Run the search demo

```shell
python3 search.py
```
