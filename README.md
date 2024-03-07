# Aerospike Vector Search (Proximus)

> [!NOTE]
> Proximus is currently in Alpha and available by invitation only. Breaking changes to our client and APIs are expected. If you want to try out Proximus, please fill out [this form](https://aerospike.com/lp/aerospike-vector-developer-program-sign-up/).

Aerospike Vector Search (Proximus) delivers an Approximate Nearest Neighbor (ANN) search using the Hierarchal Navigable Small World (HNSW) algorithm. Proximus provides a new set of capabilities and APIs for performing vector operations. This repository contains example apps for using Proximus to showcase these APIs, as well as the Python client.

Vectors allow you to combine machine learning models (e.g., ChatGPT, CLIP, Llama) to build applications that leverage the capabilities of these models. Vector embeddings encode meaning from text, images, video, etc., and enable search across a large dataset. You can use vector embeddings for a variety of applications such as semantic search, recommendation systems, or retrieval augmented generation (RAG) apps. To learn more about leveraging vector embeddings, see the OpenAI docs about [vector embedding use cases](https://platform.openai.com/docs/guides/embeddings/use-cases).

# Getting Started
This section describes how to get started using our developer sandbox environment. To request access to a developer sandbox, fill out [this form](https://aerospike.com/lp/aerospike-vector-developer-program-sign-up/). The following instructions help you set up a demo application that performs semantic search across an image dataset using the [CLIP](https://arxiv.org/abs/2103.00020) model.

## Prerequisites
You don't have to know Aerospike to get started, but you do need the following:

1. A Python 3.10 - 3.11 environment and familiarity with the Python programming language (see [Setup Python Virtual Environment](./prism-image-search/README.md#setup-python-virtual-environment)).
1. The URL to your private sandbox environment (this will be provided).

> [!TIP]
> If you are an Aerospike employee, you can follow the [docker-compose](./quote-semantic-search/README.md#install-using-docker-compose) instructions instead.

## 1. Clone the Repository and Install Dependencies

```
git clone https://github.com/aerospike/proximus-examples.git && \\
cd proximus-examples/quote-semantic-search/quote-search && \\
python3 -m pip install -r requirements.txt --extra-index-url https://aerospike.jfrog.io/artifactory/api/pypi/aerospike-pypi-dev/simple 
```

## 2. Set Environment Variables
Before starting the application, you need to set `PROXIMUS_HOST` to your sandbox host.

```
export PROXIMUS_HOST=<SANDBOX-HOST>
```
By default the app will index 5000 quotes, but the dataset included in this repo has 
over 500K quotes. Depending on the size of your dataset, you may want to configure concurrent threads for generating the image embeddings. Higher parallelism will consume more CPU resources.

```
export APP_NUM_QUOTES=500000 && \\
export APP_INDEXER_PARALLELISM=4
```

## 3. Start the Application
To start the application locally, run the following:
```
waitress-serve --host 127.0.0.1 --port 8080 --threads 32 quote_search:app
```
Quotes will begin being inferences using the [MiniLM](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) and those quotes will be added to the
index to become searchable. 


## 4. Perform a Quote Search

After starting the application, go to http://localhost:8080/search to perform a search.

The demo application enables semantic search for semantic meanings within quotes. Try using
natural language searches like "Show me quotes about the meaning of life".

# Limitations
The sandbox environment is limited to a single index. If you need to create a different index, contact us about getting a new sandbox environment. By default, each sandbox environment expires after three days.

# Contributing
If you have an idea for a sample application, open a PR and we will review it. We're excited to provide more examples of what Vector Search can do.
