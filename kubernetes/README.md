# Aerospike, Proximus, and Monitoring Deployment on GKE (Google Kubernetes Engine)

Use the scripts and manifests in this directory deploy Aerospike, Proximus, and monitoring tools on Google Kubernetes Engine (GKE).

## Prerequisites

Before you start, make sure you have installed the necessary tools:

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - Kubernetes command-line tool
- [Helm](https://helm.sh/docs/intro/install/) - Package manager for Kubernetes

## Scripts

- `full-create-and-install.sh`: Creates a GKE cluster, installs Aerospike, Proximus, and sets up monitoring services.

### Grafana Dashboards

Manage Grafana dashboards with the following commands:

- **Import Dashboards**: `./import-dashboards.sh <dashboard-dir>`
- **Local Access**: `kubectl port-forward -n monitoring svc/monitoring-stack-grafana 3000:80`

> :warning: **Warning**: Be cautious when exposing services like Grafana to the public internet. It is generally not recommended except for brief periods in a controlled testing environment. Always ensure your deployments are secured according to best practices.

- **Public Access**: `kubectl apply -f helpers/EXPOSE-GRAFANA.yaml`
- **Find Exposed Port**: `kubectl get svc grafana-loadbalancer -n monitoring`


### Additional Tools

- `helpers/aggressive-search.sh`: Executes parallel searches against the running Quote Search application using random terms.



---