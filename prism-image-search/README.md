# Prism Image Search
This is a demo application provides semantic search for a set of images
by indexing them using the [CLIP](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1)
model created by OpenAI. This model generates vectors with semantic meaning 
from each image and stores it as a vector embedding in Aerospike. When a user
performs a query a vector embedding for the provided text is generated and
Proximus performs Approximate Nearest Neighbor(ANN) search to find relevant results .

## Install with Docker Compose

The easiest way to get the demo app up and running is by using Docker compose.

To run using Docker compose:

### 1 Docker login to Aerospike's jfrog artifactory
   Your username is your email and your password is your generate jfrog identity token.
    ```shell
    docker login aerospike.jfrog.io 
    ```
### 2. Build the prism image and spin up the environment
    ```shell
    docker build -t prism . -f Dockerfile-prism
    docker compose up
    ```
### 3. Add an image dataset
To make the experience personal, you can use your own photos on your computer, or to index
a larger dataset you can browse image datasets on [Kaggle](https://www.kaggle.com/datasets).  

[This subset](https://www.kaggle.com/datasets/ifigotin/imagenetmini-1000) of the Imagenet
dataset is a good reasonable sized one (~4000 images) if you remove the `train` folder. 

Add the images you would like indexed to `container-volumes/prism/images` folder locally. 
New images added to this folder are indexed periodically. 

### 4. Perform an image search
Navigate to http://127.0.0.1:8080 and perform a search for words to find similar
images in your dataset. 

## Developing
This demo is built using [Python Flask](https://flask.palletsprojects.com/en/2.3.x/)
and [Vue.js](https://vuejs.org/). To start developing, follow the steps below to configure your Python environment.

### Configure pip
Follow [these instructions](https://github.com/citrusleaf/aerospike-proximus-client-python/tree/main#using-the-client-from-your-application-using-pip) to configure pip to use the Aerospike PyPI repository.

### Create Python Virtual Environment

```shell
# Virtual environment to isolate dependencies.
# Use your Operating system specific installation method
sudo apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```shell
python3 -m pip install -r requirements.txt
```

### Configure the Application

Set the following environment variables to configure the application. If you do not set a value for a variable, defaults are used.

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

### Configure Networking (optional)

#### Run a Proxy Server (like nginx)

Configure nginx to handle TLS as shown [here](https://dev.to/thetrebelcc/how-to-run-a-flask-app-over-https-using-waitress-and-nginx-2020-235c).

#### Start the Application

```shell
 waitress-serve --host 127.0.0.1 --port 8080 --threads 32 prism:app
```