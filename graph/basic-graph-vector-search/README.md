# Basic vector search example

A simple Python application that demonstrates Aerospike Vector and Graph Services together.

## Prerequisites

1. A Python 3.10 - 3.11 environment and familiarity with the Python programming language.
2. An Aerospike Vector Search host.
3. An Aerospike Graph Search host.

You can navigate one directory level up and refer to the README file for instructions on starting the required services.

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

Run with --help to see available the example's available configuration.
```shell
python3 search.py --help
```

Run the example.
```shell
python3 search.py
```
