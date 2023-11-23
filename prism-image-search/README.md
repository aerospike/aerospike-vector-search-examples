# Prism image search

This is a demo application
for [Aerospike Proximus](https://github.com/citrusleaf/proximus/), that indexes
images using
public embeddings models and Proximus approximate kNN search. This is an
indicative example not meant for production
use. It
uses [sentence-transformers/clip-ViT-B-32-multilingual-v1](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1)
model for image embedding.

This demo is build
using [Python Flask](https://flask.palletsprojects.com/en/2.3.x/)
and [Vue.js](https://vuejs.org/).

## Docker Compose

The easiest way to get the demo app up and running is by using docker compose.

To run using docker compose:

1. Setup pip to use Aerospike PyPI repository following instructions [here](https://github.com/citrusleaf/aerospike-proximus-client-python/tree/main#using-the-client-from-your-application-using-pip).
2. Build the prism image and spin up the environment
    ```shell
    sudo apt-get install python3-venv
    python3 -m venv .venv
    source .venv/bin/activate
    docker build -t prism . -f Dockerfile-prism
    docker compose up
    ```
3. Add the images you would like indexed to static/images/data as described in
   [How to index Images](#how-to-index-images).
4. Navigate to http://127.0.0.1:8080

## Running the demo app manually

### Prerequisites

- Aerospike Server (6+)
    - Following namespace need to be created
        - `proximus-meta` - for Proximus metadata like index definitions
        - `test` - for image records and Proximus index
- [Proximus](https://github.com/citrusleaf/proximus/) - configured to talk to
  the Aerospike cluster and running.
- Python v3.10+

### How to index images

JPEG/PNG images or directories containing images, to be indexed need to be
copied
to [images/data](static/images/data). The
application while running periodically scans and indexes the images that are not
already indexed.

### Run the application

We must set up a Python environment with the dependencies to build and run the
application

#### Setup pip
Setup pip to use Aerospike PyPI repository following instructions [here](https://github.com/citrusleaf/aerospike-proximus-client-python/tree/main#using-the-client-from-your-application-using-pip).

#### Setup Python Virtual Environment

```shell
# Virtual environment to isolate dependencies.
# Use your Operating system specific installation method
sudo apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

#### Install dependencies

```shell
python3 -m pip install -r requirements.txt
```

#### Configuration

The application can be configured by setting the following environment variable.
If not set defaults are used.

| Environment Variable        | Default            | Description                                                     |
|-----------------------------|--------------------|-----------------------------------------------------------------|
| PRISM_APP_USERNAME          |                    | If set, the username for basic authentication                   |
| PRISM_APP_USERNAME          |                    | If set, the password for basic authentication                   |
| PROXIMUS_HOST               | localhost          | Proximus server seed host                                       |
| PROXIMUS_PORT               | 5000               | Proximus server seed host port                                  |
| PROXIMUS_ADVERTISED_LISTENER|                    | An optional advertised listener to use if configured on the proximus server                              |
| PROXIMUS_NAMESPACE          | test               | The aerospike namespace for storing the image records and index |
| PROXIMUS_INDEX_NAME         | prism-image-search | The name of the  index                                          |
| PROXIMUS_MAX_RESULTS        | 20                 | Maximum number of vector search results to return               |

#### Run for demo

##### Run a proxy server like Nginx

Setup nginx to handle TLS as
shown [here](https://dev.to/thetrebelcc/how-to-run-a-flask-app-over-https-using-waitress-and-nginx-2020-235c).

##### Start the application

```shell
 waitress-serve --host 127.0.0.1 --port 8080 --threads 32 prism:app
```

#### Run for development

This mode is not recommended for demo on hosting for use. The server is known to
hang after being
idle for some time. This mode will reflect changes to the code without server
restart and hence is ideal for development.

```shell
FLASK_ENV=development FLASK_DEBUG=1 python3 -m flask --app prism  run --port 8080
```
