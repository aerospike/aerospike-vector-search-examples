# Quote Semantic search
This demo application provides semantic search for an included [dataset of quotes](https://archive.org/details/quotes_20230625)
by indexing them using the [MiniLM](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
model created by OpenAI. This model generates vectors with semantic meaning 
from each quote and stores it as a vector embedding in Aerospike. When a user
performs a query a vector embedding for the provided text is generated and
Aerospike Vector Search (AVS) performs Approximate Nearest Neighbor(ANN) search to find relevant results.


## Prerequisites
You don't have to know Aerospike to get started, but you do need the following:

1. A Python 3.10 - 3.11 environment and familiarity with the Python programming language (see [Setup Python Virtual Environment](../prism-image-search/README.md#setup-python-virtual-environment)).
1. An Aerospike Vector Search host (preview or local).

## Configure AVS host

If you are connecting to a preview environment, you'll need to set the following:
```shell
export AVS_HOST=<PREVIEW_ENV_IP>
```

## Install Dependencies
Change directories into the `quote-search` folder.

```shell
cd quote-search
```

Install dependencies using requirements.text 
```shell 
python3 -m pip install -r requirements.txt
```
## Start the application

> [!IMPORTANT]
> If you did not use an virtualenv when installing dependencies `waitress-serve` will
> likely not be in your path. 

```shell
 waitress-serve --host 127.0.0.1 --port 8080 --threads 32 quote_search:app
```

## Performing a quote search
<!-- markdown-link-check-disable-next-line -->
Navigate to http://127.0.0.1:8080/search and perform a search for quotes based on a description.


## Install using docker compose
If you have a license key, you can easily set up Aerospike, AVS, and the quote-semantic-search
app using docker-compose. 

### 1. Build the image 
```
docker build -t quote-search . -f Dockerfile-quote-search
```

### 2. Add features.conf
AVS needs an Aerospike features.conf file with the vector-search feature enabled.
Add your features.conf file to container-volumes/avs/etc/aerospike-vector-search.


### 3. Start the environment
```
docker compose up
```

## Developing
This demo is build using [Python Flask](https://flask.palletsprojects.com/en/2.3.x/)
and [Vue.js](https://vuejs.org/). In order to developer follow the steps to 
setup your Python environment.

### Setup Python Virtual Environment

```shell
# Virtual environment to isolate dependencies.
# Use your Operating system specific installation method
sudo apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```shell
cd quote-search
python3 -m pip install -r requirements.txt 
```

### Configuration

The application can be configured by setting the following environment variable.
If not set defaults are used.

| Environment Variable        | Default            | Description                                                     |
|-----------------------------|--------------------|-----------------------------------------------------------------|
| APP_USERNAME          |                    | If set, the username for basic authentication                   |
| APP_PASSWORD          |                    | If set, the password for basic authentication                   |
| APP_NUM_QUOTES                  | 5000               | The number of quotes to index. If time and space allows the max is 100000. **Hint:** To keep the app from re-indexing quotes on subsequent runs set to 0               |
| APP_INDEXER_PARALLELISM                  | 1               | To speed up indexing of quotes set this equal to or less than the number of CPU cores               |
| AVS_HOST               | localhost          | AVS server seed host                                       |
| AVS_PORT               | 5000               | AVS server seed host port                                  |
| AVS_ADVERTISED_LISTENER|                    | An optional advertised listener to use if configured on the AVS server                              |
| AVS_NAMESPACE          | test               | The aerospike namespace for storing the image records and index |
| AVS_INDEX_NAME         | quote-search       | The name of the  index                                          |
| AVS_MAX_RESULTS        | 20                 | Maximum number of vector search results to return               |
| AVS_IS_LOADBALANCER    | False                 |                 If true, the first seed address will be treated as a load balancer node.```

### Setup networking (optional)

#### Run a proxy server like Nginx

Setup nginx to handle TLS as
shown [here](https://dev.to/thetrebelcc/how-to-run-a-flask-app-over-https-using-waitress-and-nginx-2020-235c).

#### Start the application

```shell
waitress-serve --host 127.0.0.1 --port 8080 --threads 32 quote_search:app
```

#### Run for development

This mode is not recommended for demo on hosting for use. The server is known to
hang after being
idle for some time. This mode will reflect changes to the code without server
restart and hence is ideal for development.

```shell
FLASK_ENV=development FLASK_DEBUG=1 python3 -m flask --app quote_search  run --port 8080
```