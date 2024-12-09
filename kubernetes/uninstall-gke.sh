#!/bin/bash

set -eo pipefail
if [ -n "$DEBUG" ]; then set -x; fi
trap 'echo "Error: $? at line $LINENO" >&2' ERR

WORKSPACE="$(pwd)"
PROJECT_ID="$(gcloud config get-value project)"
# Prepend the current username to the cluster name
USERNAME=$(whoami)

# Default values
DEFAULT_CLUSTER_NAME_SUFFIX="avs"
RUN_INSECURE=1  # Default value for insecure mode (false meaning secure with auth + tls)

# Function to print environment variables for verification
print_env() {
    echo "Environment Variables:"
    echo "export PROJECT_ID=$PROJECT_ID"
    echo "export CLUSTER_NAME=$CLUSTER_NAME"
    echo "export NODE_POOL_NAME_AEROSPIKE=$NODE_POOL_NAME_AEROSPIKE"
    echo "export NODE_POOL_NAME_AVS=$NODE_POOL_NAME_AVS"
    echo "export ZONE=$ZONE"
    echo "export FEATURES_CONF=$FEATURES_CONF"
    echo "export CHART_LOCATION=$CHART_LOCATION"
    echo "export RUN_INSECURE=$RUN_INSECURE"
}


# Function to set environment variables
set_env_variables() {

    # Use provided cluster name or fallback to the default
    if [ -n "$CLUSTER_NAME_OVERRIDE" ]; then
        export CLUSTER_NAME="${USERNAME}-${CLUSTER_NAME_OVERRIDE}"
    else
        export CLUSTER_NAME="${USERNAME}-${PROJECT_ID}-${DEFAULT_CLUSTER_NAME_SUFFIX}"
    fi

    export NODE_POOL_NAME_AEROSPIKE="aerospike-pool"
    export NODE_POOL_NAME_AVS="avs-pool"
    export ZONE="us-central1-c"
    export FEATURES_CONF="$WORKSPACE/features.conf"
    export BUILD_DIR="$WORKSPACE/generated"
    export REVERSE_DNS_AVS
}

destroy_monitoring() {
    echo "Removing monitoring setup..."
    kubectl delete -f manifests/monitoring/avs-servicemonitor.yaml
    kubectl delete -f manifests/monitoring/aerospike-servicemonitor.yaml
    kubectl delete -f manifests/monitoring/aerospike-exporter-service.yaml

    echo "Uninstalling monitoring stack..."
    helm uninstall monitoring-stack --namespace monitoring
    kubectl delete namespace monitoring
    helm repo remove prometheus-community
}

destroy_avs_helm_chart() {
    echo "Destroying AVS Helm chart..."
    helm uninstall avs-app --namespace avs
    helm repo remove aerospike-helm
}

destroy_istio() {
    echo "Destroying Istio setup..."

    kubectl delete -f manifests/istio/avs-virtual-service.yaml
    kubectl delete -f manifests/istio/gateway.yaml

    helm uninstall istio-ingress --namespace istio-ingress
    helm uninstall istiod --namespace istio-system
    helm uninstall istio-base --namespace istio-system

    kubectl delete namespace istio-ingress
    kubectl delete namespace istio-system

    helm repo remove istio
}

destroy_avs() {
    echo "Destroying AVS secrets..."

    kubectl delete secret auth-secret --namespace avs
    kubectl delete secret aerospike-tls --namespace avs
    kubectl delete secret aerospike-secret --namespace avs
    kubectl delete namespace avs
}

destroy_aerospike() {
    echo "Destroying Aerospike setup..."

    kubectl delete -f $BUILD_DIR/manifests/aerospike-cr.yaml

    kubectl delete -f https://raw.githubusercontent.com/aerospike/aerospike-kubernetes-operator/refs/heads/master/config/samples/storage/eks_ssd_storage_class.yaml

    kubectl delete secret aerospike-secret --namespace aerospike
    kubectl delete secret auth-secret --namespace aerospike
    kubectl delete secret aerospike-tls --namespace aerospike

    kubectl delete serviceaccount aerospike-operator-controller-manager --namespace aerospike
    kubectl delete clusterrolebinding aerospike-cluster

    kubectl delete -f https://operatorhub.io/install/aerospike-kubernetes-operator.yaml

    kubectl delete namespace aerospike
}

destroy_gke_cluster() {
    echo "GKE cluster destruction..."

    gcloud container node-pools delete "$NODE_POOL_NAME_AVS" \
        --cluster "$CLUSTER_NAME" \
        --project "$PROJECT_ID" \
        --zone "$ZONE" \
        --quiet

    gcloud container node-pools delete "$NODE_POOL_NAME_AEROSPIKE" \
        --cluster "$CLUSTER_NAME" \
        --project "$PROJECT_ID" \
        --zone "$ZONE" \
        --quiet

    gcloud container clusters delete "$CLUSTER_NAME" \
        --project "$PROJECT_ID" \
        --zone "$ZONE" \
        --quiet
}


main() {
    set_env_variables
    print_env
    destroy_monitoring
    destroy_avs_helm_chart
    destroy_istio
    destroy_avs
    destroy_aerospike
    destroy_gke_cluster
}

main