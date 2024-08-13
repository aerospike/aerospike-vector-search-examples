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
python3 -m pip install -r requirements.txt
```

## Configuration

The application can be configured by setting the following command line flags.
If not set defaults are used.

[!NOTE]
It is best practice to store AVS index and record data in separate namespaces.
By default this application stores its AVS index in the "avs-index" namespace, and AVS records in "avs-data".
If your Aerospike database configuration does not define these namespaces you will see an error.
You may change the --namespace and --index-namespace to other values, like the default Aerospike "test" namespace, to use other namespaces.

| Command Line Flag        | Default            | Description                                                        |
|-----------------------------|--------------------|-----------------------------------------------------------------|
| --host               | localhost          | AVS host used for initial connection                                                   |
| --port               | 5000               | AVS server seed host port                                              |
| --namespace          | avs-data           | The Aerospike namespace for storing the quote records                  |
| --set                | basic-data         | The Aerospike set for storing the quote records                        |
| --index-namespace    | avs-index          | The Aerospike namespace for storing the HNSW index                     |
| --index-set          | basic-index        | The Aerospike set for storing the HNSW index                           |
| --load-balancer      | False              |                 If true, the first seed address will be treated as a load balancer node.```

## Run the search demo

Run with --help to see available the example's available configuration.
```shell
python3 search.py --help
```

Run the example.
```shell
python3 search.py
```
