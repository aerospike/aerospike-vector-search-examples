#!/bin/bash
export AWS_SDK_LOAD_CONFIG=1
printenv
# This script sets up a EKS cluster with configurations for Aerospike and AVS node pools.
# It handles the creation of the EKS cluster, the use of AKO (Aerospike Kubernetes Operator) to deploy an Aerospike cluster,
# deploys the AVS cluster, and the deployment of necessary operators, configurations, node pools, and monitoring.

set -eo pipefail
if [ -n "$DEBUG" ]; then set -x; fi
trap 'echo "Error: $? at line $LINENO" >&2' ERR

WORKSPACE="$(pwd)"
# Prepend the current username to the cluster name
USERNAME=$(whoami)
PROFILE="default"

# Default values
DEFAULT_CLUSTER_NAME_SUFFIX="avs"

# Function to print environment variables for verification
print_env() {
    echo "Environment Variables:"
    echo "export CLUSTER_NAME=$CLUSTER_NAME"
    echo "export NODE_POOL_NAME_AEROSPIKE=$NODE_POOL_NAME_AEROSPIKE"
    echo "export NODE_POOL_NAME_AVS=$NODE_POOL_NAME_AVS"
    echo "export REGION=$REGION"
    echo "export FEATURES_CONF=$FEATURES_CONF"
    echo "export CHART_LOCATION=$CHART_LOCATION"
    echo "export RUN_INSECURE=$RUN_INSECURE"
}

set_env_variables() {

    # Use provided cluster name or fallback to the default
    if [ -n "$CLUSTER_NAME_OVERRIDE" ]; then
        export CLUSTER_NAME="${USERNAME}-${CLUSTER_NAME_OVERRIDE}"
    else
        export CLUSTER_NAME="${USERNAME}-eks-${DEFAULT_CLUSTER_NAME_SUFFIX}"
    fi

    export NODE_POOL_NAME_AEROSPIKE="aerospike-pool"
    export NODE_POOL_NAME_AVS="avs-pool"
    export REGION="us-east-1"
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

destroy_eks_cluster() {
    echo "EKS cluster destruction..."

    eksctl delete nodegroup \
        --cluster "$CLUSTER_NAME" \
        --name "$NODE_POOL_NAME_AVS" \
        --region "$REGION" \
        --profile "$PROFILE" \
        --disable-eviction

    eksctl delete nodegroup \
        --cluster "$CLUSTER_NAME" \
        --name "$NODE_POOL_NAME_AEROSPIKE" \
        --region "$REGION" \
        --profile "$PROFILE" \
        --disable-eviction

   eksctl delete addon \
        --name aws-ebs-csi-driver \
        --cluster "$CLUSTER_NAME" \
        --region "$REGION" \
        --profile "$PROFILE"

    eksctl delete cluster \
        --name "$CLUSTER_NAME" \
        --region "$REGION" \
        --profile "$PROFILE" \
        --disable-nodegroup-eviction
}

main() {
    set_env_variables
    print_env
    destroy_monitoring
    destroy_avs_helm_chart
    destroy_istio
    destroy_avs
    destroy_aerospike
    destroy_eks_cluster
}

main