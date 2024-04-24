#!/bin/bash

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
export CLUSTER_NAME="whatthe-cluster"
export NODE_POOL_NAME_AEROSPIKE="aerospike-pool"
export NODE_POOL_NAME_PROXIMUS="proximus-pool"
export ZONE="us-central1-c"
export FEATURES_CONF="./features.conf"
export AEROSPIKE_CR="./manifests/ssd_storage_cluster_cr.yaml"

# Print environment variables to ensure they are set correctly
print_env

echo "----- Creating GKE cluster -----"
if ! gcloud container clusters create "$CLUSTER_NAME" \
      --project "$PROJECT_ID" \
      --zone "$ZONE" \
      --num-nodes 1 \
      --disk-type "pd-standard" \
      --disk-size "100"; then
    echo "Failed to create cluster"
    exit 1
else
    echo "GKE cluster created successfully."
fi

echo "----- Adding Aerospike node pool -----"
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

echo "----- Labeling and tainting Aerospike nodes -----"
kubectl get nodes -l cloud.google.com/gke-nodepool="$NODE_POOL_NAME_AEROSPIKE" -o name | \
    xargs -I {} kubectl label {} aerospike.com/node-pool=default-rack --overwrite




echo "----- Adding Proximus node pool -----"
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

echo "----- Labeling Proximus nodes -----"
kubectl get nodes -l cloud.google.com/gke-nodepool="$NODE_POOL_NAME_PROXIMUS" -o name | \
    xargs -I {} kubectl label {} aereospike.com/node-pool=proximus --overwrite

echo "----- Setup complete. The cluster and node pools are configured. -----"

echo "----- Deploying AKO -----"
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.25.0/install.sh \
| bash -s v0.25.0
kubectl create -f https://operatorhub.io/install/aerospike-kubernetes-operator.yaml

echo "----- Waiting for AKO to be ready -----"
while true; do
  if kubectl --namespace operators get deployment/aerospike-operator-controller-manager &> /dev/null; then
    echo "AKO is ready."
    kubectl --namespace operators wait \
    --for=condition=available --timeout=180s deployment/aerospike-operator-controller-manager
    break
  else
    echo "Waiting for AKO to become ready..."
    sleep 10
  fi
done

echo "----- Granting permissions to the target namespace -----"
kubectl create namespace aerospike
kubectl --namespace aerospike create serviceaccount aerospike-operator-controller-manager
kubectl create clusterrolebinding aerospike-cluster \
      --clusterrole=aerospike-cluster --serviceaccount=aerospike:aerospike-operator-controller-manager

echo "Set Secrets for Aerospike Cluster"
kubectl --namespace aerospike create secret generic aerospike-secret \
--from-file=features.conf="$FEATURES_CONF"
kubectl --namespace aerospike create secret generic auth-secret --from-literal=password='admin123'

echo "Add Storage Class"
kubectl apply -f https://raw.githubusercontent.com/aerospike/aerospike-kubernetes-operator/master/config/samples/storage/gce_ssd_storage_class.yaml

echo "Deploy Aerospike Cluster"
kubectl apply -f "$AEROSPIKE_CR"

echo "Deploy Proximus from helm chart"
# deploy proximus. this part is hacky especially until we have a public helm chart.
mkdir temp-helm
cd temp-helm
git clone -b VEC-90-helm-for-proximus https://github.com/aerospike/helm-charts.git
cd ..
helm install proximus-gke "temp-helm/helm-charts/aerospike-proximus" --values "manifests/proximus-gke-values.yaml" --namespace aerospike --wait

echo "Add monitoring"

# Add the Prometheus Community Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install the kube-prometheus-stack
helm install monitoring-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

kubectl apply -f manifests/monitoring

echo "Use the following command to view grafana dashboard"
echo "kubectl port-forward -n monitoring svc/monitoring-stack-grafana 3000:80"

echo "You can use 'import-dashboards.sh <your grafana dashboard directory>' to include your grafana dashboards"
echo "To run the quote-search app, use 'run-quote-search.sh'"

# echo "Deploy Proximus"
# helm install proximus-gke "$WORKSPACE/aerospike-proximus" \
# --values "$WORKSPACE/aerospike-proximus/examples/gke/as-proximus-gke-values.yaml" --namespace aerospike --wait
