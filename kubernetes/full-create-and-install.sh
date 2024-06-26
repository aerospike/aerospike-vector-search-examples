#!/bin/bash

# This script sets up a GKE cluster with configurations for Aerospike and AVS node pools.
# It handles the creation of the GKE cluster, the use of AKO (Aerospike Kubernetes Operator) to deploy an Aerospike cluster, deploys the AVS cluster, 
# and the deployment of necessary operators, configurations, node pools, etc.
# Additionally, it sets up monitoring using Prometheus and deploys a specific Helm chart for AVS.

# Function to print environment variables for verification
set -eo pipefail
if [ -n "$DEBUG" ]; then set -x; fi
trap 'echo "Error: $? at line $LINENO" >&2' ERR

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -f, --features-conf <features-conf>             Specify the path to the features configuration file (mandatory)"
    echo "  -r, --helm-repo <helm-repo>                     Specify the Helm repository URL (default: https://aerospike.jfrog.io/artifactory/api/helm/ecosystem-helm-dev-local)"
    echo "  -t, --docker-image-tag <docker-image-tag>       Specify the Docker image tag (default: 0.2.1)"
    echo "  -o, --docker-repo <docker-repo>                 Specify the Docker repository (default: aerospike.jfrog.io/ecosystem-container-dev-local/aerospike-proximus)"
    echo "  -c, --cluster-name <cluster-name>               Specify the GKE cluster name"
    echo "  -u, --jfrog-user <jfrog-user>                   Specify the JFrog username"
    echo "  -p, --jfrog-pass <jfrog-pass>                   Specify the JFrog password"
    echo "  -h, --help                                      Display this help message"
    exit 1
}

# Default values
export PROJECT_ID="$(gcloud config get-value project)"
export CLUSTER_NAME="${PROJECT_ID}-cluster"
export NODE_POOL_NAME_AEROSPIKE="aerospike-pool"
export NODE_POOL_NAME_AVS="avs-pool"
export ZONE="us-central1-c"
export HELM_REPO=""
export JFROG_USER=""
export JFROG_PASS=""
export DOCKER_IMAGE_TAG="0.2.0"
export DOCKER_REPO="https://artifact.aerospike.io/container/aerospike-proximus"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -f|--features-conf) FEATURES_CONF="$2"; shift ;;
        -r|--helm-repo) HELM_REPO="$2"; shift ;;
        -t|--docker-image-tag) DOCKER_IMAGE_TAG="$2"; shift ;;
        -o|--docker-repo) DOCKER_REPO="$2"; shift ;;
        -c|--cluster-name) CLUSTER_NAME="$2"; shift ;;
        -u|--jfrog-user) JFROG_USER="$2"; shift ;;
        -p|--jfrog-pass) JFROG_PASS="$2"; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done

# Check if mandatory argument is set
if [ -z "$FEATURES_CONF" ]; then
    echo "Error: a valid feature file must be provided (--features-conf)."
    usage
fi

# Check if the features configuration file exists
if [ ! -f "$FEATURES_CONF" ]; then
    echo "Error: The features configuration file '$FEATURES_CONF' does not exist."
    exit 1
fi

# Check Docker login
echo "Checking Docker login to aerospike.jfrog.io..."
if ! echo "$JFROG_PASS" | docker login aerospike.jfrog.io -u "$JFROG_USER" --password-stdin; then
    echo "Error: Invalid credentials for '$JFROG_USER'."
    exit 1
else
    echo "Docker login succeeds."
fi

echo "Starting GKE cluster creation..."
if ! gcloud container clusters create "$CLUSTER_NAME" \
      --project "$PROJECT_ID" \
      --zone "$ZONE" \
      --num-nodes 1 \
      --disk-type "pd-standard" \
      --disk-size "100"; then
    echo "Failed to create GKE cluster"
    exit 1
else
    echo "GKE cluster created successfully."
fi

echo "Creating Aerospike node pool..."
if ! gcloud container node-pools create "$NODE_POOL_NAME_AEROSPIKE" \
      --cluster "$CLUSTER_NAME" \
      --project "$PROJECT_ID" \
      --zone "$ZONE" \
      --num-nodes 3 \
      --local-ssd-count 2 \
      --disk-type "pd-standard" \
      --disk-size "100" \
      --machine-type "n2d-standard-2"; then
    echo "Failed to create Aerospike node pool"
    exit 1
else
    echo "Aerospike node pool added successfully."
fi

echo "Labeling Aerospike nodes..."
kubectl get nodes -l cloud.google.com/gke-nodepool="$NODE_POOL_NAME_AEROSPIKE" -o name | \
    xargs -I {} kubectl label {} aerospike.com/node-pool=default-rack --overwrite

echo "Deploying Aerospike Kubernetes Operator (AKO)..."
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.25.0/install.sh | bash -s v0.25.0
kubectl create -f https://operatorhub.io/install/aerospike-kubernetes-operator.yaml

echo "Waiting for AKO to be ready..."
while true; do
  if kubectl --namespace operators get deployment/aerospike-operator-controller-manager &> /dev/null; then
    echo "AKO is ready."
    kubectl --namespace operators wait \
    --for=condition=available --timeout=180s deployment/aerospike-operator-controller-manager
    break
  else
    echo "AKO setup is still in progress..."
    sleep 10
  fi
done

echo "Granting permissions to the target namespace..."
kubectl create namespace aerospike
kubectl --namespace aerospike create serviceaccount aerospike-operator-controller-manager
kubectl create clusterrolebinding aerospike-cluster \
      --clusterrole=aerospike-cluster --serviceaccount=aerospike:aerospike-operator-controller-manager

echo "Setting secrets for Aerospike cluster..."
kubectl --namespace aerospike create secret generic aerospike-secret --from-file=features.conf="$FEATURES_CONF"
kubectl --namespace aerospike create secret generic auth-secret --from-literal=password='admin123'

echo "Adding storage class..."
kubectl apply -f https://raw.githubusercontent.com/aerospike/aerospike-kubernetes-operator/master/config/samples/storage/gce_ssd_storage_class.yaml

echo "Deploying Aerospike cluster..."
kubectl apply -f https://raw.githubusercontent.com/aerospike/aerospike-vector-search-examples/main/kubernetes/manifests/ssd_storage_cluster_cr.yaml


############################################## 
# AVS namespace
##############################################

echo "Adding AVS node pool..."
if ! gcloud container node-pools create "$NODE_POOL_NAME_AVS" \
      --cluster "$CLUSTER_NAME" \
      --project "$PROJECT_ID" \
      --zone "$ZONE" \
      --num-nodes 3 \
      --disk-type "pd-standard" \
      --disk-size "100" \
      --machine-type "e2-highmem-4"; then
    echo "Failed to create AVS node pool"
    exit 1
else
    echo "AVS node pool added successfully."
fi

echo "Labeling AVS nodes..."
kubectl get nodes -l cloud.google.com/gke-nodepool="$NODE_POOL_NAME_AVS" -o name | \
    xargs -I {} kubectl label {} aerospike.com/node-pool=avs --overwrite

echo "Setup complete. Cluster and node pools are configured."

kubectl create namespace avs

echo "Setting secrets for AVS cluster..."
kubectl --namespace avs create secret generic aerospike-secret --from-file=features.conf="$FEATURES_CONF"
kubectl --namespace avs create secret generic auth-secret --from-literal=password='admin123'


kubectl create secret docker-registry private-docker \
        --namespace avs \
        --docker-server=aerospike.jfrog.io \
        --docker-username=$JFROG_USER  \
        --docker-password=$JFROG_PASS \
        --docker-email=$JFROG_USER

###################################################
# Optional add Istio
###################################################
echo "Deploying Istio"
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

helm install istio-base istio/base --namespace istio-system --set defaultRevision=default --create-namespace --wait
helm install istiod istio/istiod --namespace istio-system --create-namespace --wait
helm install istio-ingress istio/gateway \
 --values ./manifests/istio/istio-ingressgateway-values.yaml \
 --namespace istio-ingress \
 --create-namespace \
 --wait

kubectl apply -f manifests/istio/gateway.yaml
kubectl apply -f manifests/istio/avs-virtual-service.yaml

###################################################
# End Istio
###################################################


#helm repo add aerospike-helm https://artifact.aerospike.io/artifactory/api/helm/aerospike-helm
helm repo add ecosystem-helm-dev-local "$HELM_REPO" --username "$JFROG_USER" --password "$JFROG_PASS"
helm repo update
helm install avs-gke --values "manifests/avs-gke-values.yaml" --namespace avs ecosystem-helm-dev-local/aerospike-vector-search \
        --set image.repository=aerospike.jfrog.io/ecosystem-container-dev-local/aerospike-proximus \
        --set image.tag=$DOCKER_IMAGE_TAG \
        --set imagePullSecrets[0].name=private-docker \
      --version 0.2.1
  
  #helm install avs-gke --values "manifests/avs-gke-values.yaml" --namespace avs aerospike-helm/aerospike-vector-search --wait

##############################################
# Monitoring namespace
##############################################
echo "Adding monitoring setup..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

echo "Applying additional monitoring manifests..."
kubectl apply -f manifests/monitoring/aerospike-exporter-service.yaml
kubectl apply -f manifests/monitoring/aerospike-servicemonitor.yaml
kubectl apply -f manifests/monitoring/avs-servicemonitor.yaml



echo "Setup complete."
echo "To include your Grafana dashboards, use 'import-dashboards.sh <your grafana dashboard directory>'"

echo "To view Grafana dashboards from your machine use 'kubectl port-forward -n monitoring svc/monitoring-stack-grafana 3000:80'"
echo "To expose Grafana ports publicly, use 'kubectl apply -f helpers/EXPOSE-GRAFANA.yaml'"
echo "To find the exposed port, use 'kubectl get svc -n monitoring'"

echo "To run the quote search sample app on your new cluster, for istio use:"
echo "helm install semantic-search-app aerospike/quote-semantic-search --namespace avs --values manifests/quote-search/semantic-search-values.yaml --wait"

#Instalation successful
kubectl get pods -n avs

kubectl get svc -n istio-ingress
