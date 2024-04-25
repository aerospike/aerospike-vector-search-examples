Use the scripts and manifests in this directory to deploy Aerospike, Proximus, and monitoring on GKE (Google Kubernetes Engine).

## Prerequisites
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [helm](https://helm.sh/docs/intro/install/)
 
The script `full-create-and-install.sh` will create a GKE cluster, install Aerospike, Proximus, and monitoring.

The script `run-quote-search.sh` will run the Quote Search sample application.

`helpers/agressive-search.sh` will run searches in parallel against a running Quote Search application using random terms.
`EXPOSE_GRAFANA` will expose Grafana to the internet. This is not recommended except for testing.