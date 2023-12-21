# Basic vector search example

A simple python application that demonstrates vector ANN index creation, vector record insertion and basic ANN query
against Proximus server, using the python client.

## Prerequisites

See the prerequisites [here](https://github.com/citrusleaf/aerospike-proximus-client-python/tree/main#prerequisites)

## Setup pip PyPI repository

Setup pip to use Aerospike PyPI repository following
instructions [here](https://github.com/citrusleaf/aerospike-proximus-client-python/tree/main#using-the-client-from-your-application-using-pip).

## Setup build Python Virtual Environment

This is the recommended mode for building the python client.

```shell
# Create virtual environment to isolate dependencies.
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```shell
python3 -m pip install -r requirements.txt
```

## Run the search demo

```shell
python3 search.py
```