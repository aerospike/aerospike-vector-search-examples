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
> If you are an Aerospike employee, you can follow the [docker-compose](./prism-image-search/README.md#install-using-docker-compose) instructions instead.

## 1. Clone the Repository and Install Dependencies

```
git clone https://github.com/aerospike/proximus-examples.git && \\
cd proximus-examples/prism-image-search/prism && \\
python3 -m pip install -r requirements.txt --extra-index-url https://aerospike.jfrog.io/artifactory/api/pypi/aerospike-pypi-dev/simple 
```

## 2. Find an Image Dataset to Index

The demo application indexes images stored on your computer and generates vector embeddings that are sent to a Proximus server hosted in the cloud. To personalize the demo, you can use your own photos if you like. To index a larger dataset, you can browse image datasets available on [Kaggle](https://www.kaggle.com/datasets).  

[This subset](https://www.kaggle.com/datasets/ifigotin/imagenetmini-1000) of the Imagenet
dataset is reasonably sized (~4000 images) if you remove the `train` folder.

> [!NOTE]
> The images from your dataset do not leave your local environment, but the vector embeddings
> are sent to our sandbox environment. All data is destroyed after three days.

After you have identified a dataset of images (must be JPEGs), copy them to `prism/static/images/data`.

## 3. Set Environment Variables
Before starting the application, you need to set `PROXIMUS_HOST` to your sandbox host.

```
export PROXIMUS_HOST=<SANDBOX-HOST>
```
Depending on the size of your dataset, you may want to configure concurrent threads for generating the image embeddings. Higher parallelism will consume more CPU resources.

```
export APP_INDEXER_PARALLELISM=4
```

## 4. Start the Application
To start the application locally, run the following:
```
waitress-serve --host 127.0.0.1 --port 8080 --threads 32 prism:app
```
Images are read and indexed using the CLIP model, indicated by a progress bar. Depending on the size of your dataset, it may take a few minutes to a few hours to index your images.

## 5. Perform an Image Search

After starting the application, go to http://localhost:8080/search to perform a search.

The demo application enables semantic search for a set of images by indexing them using the [CLIP](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1) model created by OpenAI. This model generates vectors with semantic meaning from each image and stores them as vector embeddings in Aerospike. When a user submits a query, Proximus generates a vector embedding for the provided text and performs an Approximate Nearest Neighbor (ANN) search to find relevant results.

# Limitations
The sandbox environment is limited to a single index. If you need to create a different index, contact us about getting a new sandbox environment. By default, each sandbox environment expires after three days.

# Contributing
If you have an idea for a sample application, open a PR and we will review it. We're excited to provide more examples of what Vector Search can do.
