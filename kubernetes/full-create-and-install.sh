#!/bin/bash

# This script sets up a GKE cluster with specific configurations for Aerospike and Proximus node pools.
# It handles the creation of the cluster, node pools, labeling, tainting of nodes, and deployment of necessary operators and configurations.
# Additionally, it sets up monitoring using Prometheus and deploys a specific Helm chart for Proximus.

# Function to print environment variables for verification
print_env() {
    echo "Environment Variables:"
    echo "export PROJECT_ID=$PROJECT_ID"
    echo "export CLUSTER_NAME=$CLUSTER_NAME"
    echo "export NODE_POOL_NAME_AEROSPIKE=$NODE_POOL_NAME_AEROSPIKE"
    echo "export NODE_POOL_NAME_PROXIMUS=$NODE_POOL_NAME_PROXIMUS"
    echo "export ZONE=$ZONE"
    echo "export FEATURES_CONF=$FEATURES_CONF"
    echo "export AEROSPIKE_CR=$AEROSPIKE_CR"
}

# Set environment variables for the GKE cluster setup
export PROJECT_ID="aerostation-dev"
export CLUSTER_NAME="my-world"
export NODE_POOL_NAME_AEROSPIKE="aerospike-pool"
export NODE_POOL_NAME_PROXIMUS="proximus-pool"
export ZONE="us-central1-c"
export FEATURES_CONF="./features.conf"
export AEROSPIKE_CR="./manifests/ssd_storage_cluster_cr.yaml"

# Print environment variables to ensure they are set correctly
print_env

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting GKE cluster creation..."
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

# This does not work for some reason, suspecting bad label
# kubectl get nodes -l cloud.google.com/gke-nodepool="$NODE_POOL_NAME_AEROSPIKE" -o name | \
#     xargs -I {} kubectl taint nodes {} dedicated=aerospike:NoSchedule --overwrite

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
kubectl apply -f "$AEROSPIKE_CR"
############################################## 
# Proximus name space
##############################################

echo "Adding Proximus node pool..."
if ! gcloud container node-pools create "$NODE_POOL_NAME_PROXIMUS" \
      --cluster "$CLUSTER_NAME" \
      --project "$PROJECT_ID" \
      --zone "$ZONE" \
      --num-nodes 3 \
      --disk-type "pd-standard" \
      --disk-size "100" \
      --machine-type "e2-highmem-4"; then
    echo "Failed to create Proximus node pool"
    exit 1
else
    echo "Proximus node pool added successfully."
fi

echo "Labeling Proximus nodes..."
kubectl get nodes -l cloud.google.com/gke-nodepool="$NODE_POOL_NAME_PROXIMUS" -o name | \
    xargs -I {} kubectl label {} aerospike.com/node-pool=proximus --overwrite



echo "Setup complete. Cluster and node pools are configured."

kubectl create namespace proximus

echo "Setting secrets for proximus cluster..."
kubectl --namespace proximus create secret generic aerospike-secret --from-file=features.conf="$FEATURES_CONF"
kubectl --namespace proximus create secret generic auth-secret --from-literal=password='admin123'


# replace with helm repo add when helm chart is published. 
# echo "Deploying Proximus from Helm chart..."
# mkdir -p temp-helm
# cd temp-helm
# git clone  https://github.com/aerospike/helm-charts.git
# cd ..

helm install proximus-gke --values "manifests/proximus-gke-values.yaml" --namespace proximus aerospike/aerospike-proximus --wait


##############################################
# Monitoring namespace
##############################################
echo "Adding monitoring setup..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

echo "Applying additional monitoring manifests..."
kubectl apply -f manifests/monitoring

echo "Setup complete."
echo "To include your Grafana dashboards, use 'import-dashboards.sh <your grafana dashboard directory>'"

echo "To view grafana dashboards from your machine use kubectl port-forward -n monitoring svc/monitoring-stack-grafana 3000:80"
echo "To expose grafana ports publically 'kubectl apply -f helpers/EXPOSE-GRAFANA.yaml'"
echo "To find the exposed port with 'kubectl get svc -n monitoring' " 


To run the quote search sample app on your new cluster you can use 
   helm install sematic-search-app  aerospike/quote-semantic-search --namespace proximus --values manifests/sematic-search-values.yaml --wait

