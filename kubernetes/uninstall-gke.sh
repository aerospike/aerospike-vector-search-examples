#!/bin/bash

# This script uninstalls the resources created by the full-create-and-install-gke.sh script.
# It handles the removal of deployments, services, namespaces, node pools, and optionally the GKE cluster itself.

set -eo pipefail
if [ -n "$DEBUG" ]; then set -x; fi
trap 'echo "Error: $? at line $LINENO" >&2' ERR

WORKSPACE="$(pwd)"
PROJECT_ID="$(gcloud config get-value project)"
# Prepend the current username to the cluster name
USERNAME=$(whoami)

# Default values
DEFAULT_CLUSTER_NAME_SUFFIX="avs"
DESTROY_CLUSTER=1  # Default is to destroy the cluster

# Function to display the script usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --cluster-name, -c <name>    Override the default cluster name (default: ${USERNAME}-${PROJECT_ID}-${DEFAULT_CLUSTER_NAME_SUFFIX})"
    echo "  --keep-cluster, -k           Do not destroy the GKE cluster. No argument required."
    echo "  --help, -h                   Show this help message"
    exit 1
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --cluster-name|-c) CLUSTER_NAME_OVERRIDE="$2"; shift 2 ;;
        --keep-cluster|-k) DESTROY_CLUSTER=0; shift ;;
        --help|-h) usage ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
done

# Function to print environment variables for verification
print_env() {
    echo "Environment Variables:"
    echo "export PROJECT_ID=$PROJECT_ID"
    echo "export CLUSTER_NAME=$CLUSTER_NAME"
    echo "export NODE_POOL_NAME_AEROSPIKE=$NODE_POOL_NAME_AEROSPIKE"
    echo "export NODE_POOL_NAME_AVS=$NODE_POOL_NAME_AVS"
    echo "export ZONE=$ZONE"
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
    export BUILD_DIR="$WORKSPACE/generated"
}


destroy_monitoring() {
    if kubectl get ns monitoring &> /dev/null; then
        kubectl delete -f manifests/monitoring/avs-servicemonitor.yaml --namespace monitoring || true
        kubectl delete -f manifests/monitoring/aerospike-servicemonitor.yaml --namespace monitoring || true
        kubectl delete -f manifests/monitoring/aerospike-exporter-service.yaml --namespace monitoring || true
        helm uninstall monitoring-stack --namespace monitoring || true
        kubectl delete ns monitoring || true
    fi
    helm repo remove prometheus-community || true
}


destroy_avs_helm_chart() {
    helm uninstall avs-app-query --namespace avs || true
    helm uninstall avs-app-update --namespace avs || true
    helm uninstall avs-gke --namespace avs || true # For backwards compatibility
    helm repo remove aerospike-helm || true
}

destroy_istio() {
    kubectl delete -f manifests/istio/avs-virtual-service.yaml --namespace istio-ingress || true
    kubectl delete -f manifests/istio/gateway.yaml || true

    helm uninstall istio-ingress --namespace istio-ingress || true
    helm uninstall istiod --namespace istio-system || true
    helm uninstall istio-base --namespace istio-system || true

    kubectl delete ns istio-ingress || true
    kubectl delete ns istio-system || true
    helm repo remove istio || true
}

destroy_avs() {
    kubectl delete secret auth-secret --namespace avs || true
    kubectl delete secret aerospike-tls --namespace avs || true
    kubectl delete secret aerospike-secret --namespace avs || true
    kubectl delete ns avs || true
}

destroy_aerospike() {
    kubectl delete -f "$BUILD_DIR/manifests/aerospike-cr.yaml" --namespace aerospike || true
    kubectl delete -f "https://raw.githubusercontent.com/aerospike/aerospike-kubernetes-operator/master/config/samples/storage/gce_ssd_storage_class.yaml" || true

    kubectl delete secret aerospike-secret --namespace aerospike || true
    kubectl delete secret auth-secret --namespace aerospike || true
    kubectl delete secret aerospike-tls --namespace aerospike || true

    kubectl delete serviceaccount aerospike-operator-controller-manager --namespace aerospike || true
    kubectl delete clusterrolebinding aerospike-cluster || true

    kubectl delete -f "https://operatorhub.io/install/aerospike-kubernetes-operator.yaml" || true
    kubectl delete ns aerospike || true
}

destroy_gke_cluster() {
    if [[ "$DESTROY_CLUSTER" -eq 1 ]]; then
        echo "GKE cluster destruction..."

        gcloud container node-pools delete "$NODE_POOL_NAME_AVS" \
            --cluster "$CLUSTER_NAME" \
            --project "$PROJECT_ID" \
            --zone "$ZONE" \
            --quiet || true

        gcloud container node-pools delete "$NODE_POOL_NAME_AEROSPIKE" \
            --cluster "$CLUSTER_NAME" \
            --project "$PROJECT_ID" \
            --zone "$ZONE" \
            --quiet || true

        gcloud container clusters delete "$CLUSTER_NAME" \
            --project "$PROJECT_ID" \
            --zone "$ZONE" \
            --quiet || true
    else
        echo "Skipping GKE cluster destruction due to --keep-cluster flag."
    fi
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

