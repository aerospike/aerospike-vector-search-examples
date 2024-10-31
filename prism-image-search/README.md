# Prism image search
This demo application provides semantic search for a set of images
by indexing them using the [CLIP](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1)
model created by OpenAI. This model generates vectors with semantic meaning 
from each image and stores it as a vector embedding in Aerospike. When a user
performs a query a vector embedding for the provided text is generated and
Aerospike Vector Search (AVS) performs Approximate Nearest Neighbor(ANN) search to find relevant results .

## Prerequisites
You don't have to know Aerospike to get started, but you do need the following:

1. A Python 3.10 - 3.11 environment and familiarity with the Python programming language (see [Setup Python Virtual Environment](./README.md#setup-python-virtual-environment)).
2. An Aerospike Vector Search host (preview environment or local) running AVS 0.11.1 or newer.

## Configure AVS host

If you are connecting to a preview environment, you'll need to set the following:
```shell
export AVS_HOST=<PREVIEW_ENV_IP>
```

## Install Dependencies
Change directories into the `prism` folder.

```shell
cd prism
```

Install dependencies using requirements.text 
```shell 
python3 -m pip install -r requirements.txt
```
## Link your photos
To index your local photos, create a symlink to a location with photos directory.

```shell
ln -s ~/Pictures static/images/data
```
## Start the application

> [!IMPORTANT]
> If you did not use an virtualenv when installing dependencies `waitress-serve` will
> likely not be in your path. 

```shell
 waitress-serve --host 127.0.0.1 --port 8080 --threads 32 prism:app
```

## Performing an image search
<!-- markdown-link-check-disable-next-line -->
Navigate to http://127.0.0.1:8080 and perform a search for images based on a
description.


## Install using docker compose
If you have a license key, you can easily setup Aerospike, AVS, and the prism-image-search
app using docker-compose. When using docker-compose, you'll need to place your images in `container-volumes/prism/images/static/data`

```shell
ln -s ~/Pictures container-volumes/prism/images/static/data
```

### 1. Build the prism image 
```
cd prism-image-search && \\
docker build -t prism . -f Dockerfile-prism
```

### 2. Add features.conf
AVS needs an Aerospike features.conf file with the vector-search feature enabled.
Add your features.conf file to `container-volumes/avs/etc/aerospike-vector-search`.

### 3. Start the environment
```
docker compose -f docker-compose-dev.yml up
```

## Developing
This demo is built using [Python Flask](https://flask.palletsprojects.com/en/2.3.x/)
and [Vue.js](https://vuejs.org/). To start developing, follow the steps to 
set up your Python environment.

### Set up Python Virtual Environment

```shell
# Virtual environment to isolate dependencies.
# Use your Operating system specific installation method
sudo apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```shell
cd prism
python3 -m pip install -r requirements.txt
```

### Configuration

The application can be configured by setting the following environment variable.
If not set defaults are used.

[!NOTE]
It is best practice to store AVS index and record data in separate namespaces.
By default this application stores its AVS index in the "avs-index" namespace, and AVS records in "avs-data".
If your Aerospike database configuration does not define these namespaces you will see an error.
You may change the AVS_NAMESPACE and AVS_INDEX_NAMESPACE to other values, like the default Aerospike "test" namespace, to use other namespaces.

[!NOTE]
Using a load balancer with AVS is best practice. Therefore AVS_IS_LOADBAlANCER defaults to True.
This works fine for AVS clusters with a load balancer or clusters with only 1 node. If you are using
the examples with an AVS cluster larger than 1 node without load balancing you should set AVS_IS_LOADBAlANCER to False.


| Environment Variable   | Default            | Description                                                     |
|------------------------|--------------------|-----------------------------------------------------------------|
| APP_USERNAME           |                    | If set, the username for basic authentication                   |
| APP_PASSWORD           |                    | If set, the password for basic authentication                   |
| APP_INDEXER_PARALLELISM| 1                  | To speed up indexing of quotes set this equal to or less than the number of CPU cores               |
| AVS_HOST               | localhost          | AVS server seed host                                            |
| AVS_PORT               | 5000               | AVS server seed host port                                       |
| AVS_ADVERTISED_LISTENER|                    | An optional advertised listener to use if configured on the AVS server                              |
| AVS_NAMESPACE     | avs-data               | The Aerospike namespace for storing the image records           |
| AVS_SET           | image-data         | The Aerospike set for storing the image records                 |
| AVS_INDEX_NAMESPACE     | avs-index               | The Aerospike namespace for storing the HNSW index              |
| AVS_INDEX_SET           | image-index        | The Aerospike set for storing the HNSW index                    |
| AVS_INDEX_NAME         | prism-image-search | The name of the  index                                          |
| AVS_MAX_RESULTS        | 20                 | Maximum number of vector search results to return               |
| AVS_IS_LOADBALANCER    | True              |                 If true, the first seed address will be treated as a load balancer node.```

### Setup networking (optional)

#### Run a proxy server like Nginx

Setup nginx to handle TLS as
shown [here](https://dev.to/thetrebelcc/how-to-run-a-flask-app-over-https-using-waitress-and-nginx-2020-235c).


#### Run for development

This mode is not recommended for demo on hosting for use. The server is known to
hang after being
idle for some time. This mode will reflect changes to the code without server
restart and hence is ideal for development.

```shell
FLASK_ENV=development FLASK_DEBUG=1 python3 -m flask --app prism  run --port 8080
```