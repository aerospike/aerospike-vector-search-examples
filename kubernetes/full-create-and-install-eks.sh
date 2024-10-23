#!/bin/bash
export AWS_SDK_LOAD_CONFIG=1
printenv
# This script sets up a GKE cluster with configurations for Aerospike and AVS node pools.
# It handles the creation of the GKE cluster, the use of AKO (Aerospike Kubernetes Operator) to deploy an Aerospike cluster,
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
RUN_INSECURE=1  # Default value for insecure mode (false meaning secure with auth + tls)

# Function to display the script usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --chart-location, -l <path>  If specified expects a local directory for AVS Helm chart (default: official repo)"
    echo "  --cluster-name, -c <name>    Override the default cluster name (default: ${USERNAME}-${PROJECT_ID}-${DEFAULT_CLUSTER_NAME_SUFFIX})"
    echo "  --run-insecure, -r           Run setup cluster without auth or tls. No argument required."
    echo "  --help, -h                   Show this help message"
    exit 1
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --chart-location|-l) CHART_LOCATION="$2"; shift 2 ;;
        --cluster-name|-c) CLUSTER_NAME_OVERRIDE="$2"; shift 2 ;;
        --run-insecure|-r) RUN_INSECURE=1; shift ;;   # just flag no argument
        --help|-h) usage ;;  # Display the help/usage if --help or -h is passed
        *) echo "Unknown parameter passed: $1"; usage ;;  # Unknown parameter triggers usage
    esac
done

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


# Function to set environment variables
set_env_variables() {
   
    # Use provided cluster name or fallback to the default
    if [ -n "$CLUSTER_NAME_OVERRIDE" ]; then
        export CLUSTER_NAME="${USERNAME}-${CLUSTER_NAME_OVERRIDE}"
    else
        export CLUSTER_NAME="${USERNAME}-eks-${DEFAULT_CLUSTER_NAME_SUFFIX}"
    fi

    export NODE_POOL_NAME_AEROSPIKE="aerospike-pool"
    export NODE_POOL_NAME_AVS="avs-pool"
    export REGION="eu-central-1"
    export FEATURES_CONF="$WORKSPACE/features.conf"
    export BUILD_DIR="$WORKSPACE/generated"
}

reset_build() {
    if [ -d "$BUILD_DIR" ]; then
        temp_dir=$(mktemp -d /tmp/avs-deploy-previous.XXXXXX)
        mv -f "$BUILD_DIR" "$temp_dir"
    fi
    mkdir -p "$BUILD_DIR/input" "$BUILD_DIR/output" "$BUILD_DIR/secrets" "$BUILD_DIR/certs" "$BUILD_DIR/manifests"
    cp "$FEATURES_CONF" "$BUILD_DIR/secrets/features.conf"
    if [[ "${RUN_INSECURE}" == 1 ]]; then
        cp $WORKSPACE/manifests/avs-gke-values.yaml $BUILD_DIR/manifests/avs-gke-values.yaml
        cp $WORKSPACE/manifests/aerospike-cr.yaml $BUILD_DIR/manifests/aerospike-cr.yaml
    else
        cp $WORKSPACE/manifests/avs-gke-values-auth.yaml $BUILD_DIR/manifests/avs-gke-values.yaml
        cp $WORKSPACE/manifests/aerospike-cr-auth.yaml $BUILD_DIR/manifests/aerospike-cr.yaml
    fi
}

generate_certs() {
    echo "Generating certificates..."
    # cp -r $WORKSPACE/certs $BUILD_DIR/certs
    echo "Generate Root"
    openssl genrsa \
    -out "$BUILD_DIR/output/ca.aerospike.com.key" 2048

    openssl req \
    -x509 \
    -new \
    -nodes \
    -config "$WORKSPACE/ssl/openssl_ca.conf" \
    -extensions v3_ca \
    -key "$BUILD_DIR/output/ca.aerospike.com.key" \
    -sha256 \
    -days 3650 \
    -out "$BUILD_DIR/output/ca.aerospike.com.pem" \
    -subj "/C=UK/ST=London/L=London/O=abs/OU=Support/CN=ca.aerospike.com"

    echo "Generate Requests & Private Key"
    SVC_NAME="aerospike-cluster.aerospike.svc.cluster.local" COMMON_NAME="asd.aerospike.com" openssl req \
    -new \
    -nodes \
    -config "$WORKSPACE/ssl/openssl.conf" \
    -extensions v3_req \
    -out "$BUILD_DIR/input/asd.aerospike.com.req" \
    -keyout "$BUILD_DIR/output/asd.aerospike.com.key" \
    -subj "/C=UK/ST=London/L=London/O=abs/OU=Server/CN=asd.aerospike.com"

    SVC_NAME="avs-gke-aerospike-vector-search.aerospike.svc.cluster.local" COMMON_NAME="avs.aerospike.com" openssl req \
    -new \
    -nodes \
    -config "$WORKSPACE/ssl/openssl.conf" \
    -extensions v3_req \
    -out "$BUILD_DIR/input/avs.aerospike.com.req" \
    -keyout "$BUILD_DIR/output/avs.aerospike.com.key" \
    -subj "/C=UK/ST=London/L=London/O=abs/OU=Client/CN=avs.aerospike.com" \

    SVC_NAME="avs-gke-aerospike-vector-search.aerospike.svc.cluster.local" COMMON_NAME="svc.aerospike.com" openssl req \
    -new \
    -nodes \
    -config "$WORKSPACE/ssl/openssl_svc.conf" \
    -extensions v3_req \
    -out "$BUILD_DIR/input/svc.aerospike.com.req" \
    -keyout "$BUILD_DIR/output/svc.aerospike.com.key" \
    -subj "/C=UK/ST=London/L=London/O=abs/OU=Client/CN=svc.aerospike.com" \

    echo "Generate Certificates"
    SVC_NAME="aerospike-cluster.aerospike.svc.cluster.local" COMMON_NAME="asd.aerospike.com" openssl x509 \
    -req \
    -extfile "$WORKSPACE/ssl/openssl.conf" \
    -in "$BUILD_DIR/input/asd.aerospike.com.req" \
    -CA "$BUILD_DIR/output/ca.aerospike.com.pem" \
    -CAkey "$BUILD_DIR/output/ca.aerospike.com.key" \
    -extensions v3_req \
    -days 3649 \
    -outform PEM \
    -out "$BUILD_DIR/output/asd.aerospike.com.pem" \
    -set_serial 110 \

    SVC_NAME="avs-gke-aerospike-vector-search.aerospike.svc.cluster.local" COMMON_NAME="avs.aerospike.com" openssl x509 \
    -req \
    -extfile "$WORKSPACE/ssl/openssl.conf" \
    -in "$BUILD_DIR/input/avs.aerospike.com.req" \
    -CA "$BUILD_DIR/output/ca.aerospike.com.pem" \
    -CAkey "$BUILD_DIR/output/ca.aerospike.com.key" \
    -extensions v3_req \
    -days 3649 \
    -outform PEM \
    -out "$BUILD_DIR/output/avs.aerospike.com.pem" \
    -set_serial 210 \

    SVC_NAME="avs-gke-aerospike-vector-search.aerospike.svc.cluster.local" COMMON_NAME="svc.aerospike.com" openssl x509 \
    -req \
    -extfile "$WORKSPACE/ssl/openssl_svc.conf" \
    -in "$BUILD_DIR/input/svc.aerospike.com.req" \
    -CA "$BUILD_DIR/output/ca.aerospike.com.pem" \
    -CAkey "$BUILD_DIR/output/ca.aerospike.com.key" \
    -extensions v3_req \
    -days 3649 \
    -outform PEM \
    -out "$BUILD_DIR/output/svc.aerospike.com.pem" \
    -set_serial 310 \

    echo "Verify Certificate signed by root"
    openssl verify \
    -verbose \
    -CAfile "$BUILD_DIR/output/ca.aerospike.com.pem" \
    "$BUILD_DIR/output/asd.aerospike.com.pem"

    openssl verify \
    -verbose\
    -CAfile "$BUILD_DIR/output/ca.aerospike.com.pem" \
    "$BUILD_DIR/output/asd.aerospike.com.pem"

    openssl verify \
    -verbose\
    -CAfile "$BUILD_DIR/output/ca.aerospike.com.pem" \
    "$BUILD_DIR/output/svc.aerospike.com.pem"

    PASSWORD="citrusstore"
    echo -n "$PASSWORD" | tee "$BUILD_DIR/output/storepass" \
    "$BUILD_DIR/output/keypass" > \
    "$BUILD_DIR/secrets/client-password.txt"

    ADMIN_PASSWORD="admin123"
    echo -n "$ADMIN_PASSWORD" > "$BUILD_DIR/secrets/aerospike-password.txt"

    keytool \
    -import \
    -file "$BUILD_DIR/output/ca.aerospike.com.pem" \
    --storepass "$PASSWORD" \
    -keystore "$BUILD_DIR/output/ca.aerospike.com.truststore.jks" \
    -alias "ca.aerospike.com" \
    -noprompt

    openssl pkcs12 \
    -export \
    -out "$BUILD_DIR/output/avs.aerospike.com.p12" \
    -in "$BUILD_DIR/output/avs.aerospike.com.pem" \
    -inkey "$BUILD_DIR/output/avs.aerospike.com.key" \
    -password file:"$BUILD_DIR/output/storepass"

    keytool \
    -importkeystore \
    -srckeystore "$BUILD_DIR/output/avs.aerospike.com.p12" \
    -destkeystore "$BUILD_DIR/output/avs.aerospike.com.keystore.jks" \
    -srcstoretype pkcs12 \
    -srcstorepass "$(cat $BUILD_DIR/output/storepass)" \
    -deststorepass "$(cat $BUILD_DIR/output/storepass)" \
    -noprompt

    openssl pkcs12 \
    -export \
    -out "$BUILD_DIR/output/svc.aerospike.com.p12" \
    -in "$BUILD_DIR/output/svc.aerospike.com.pem" \
    -inkey "$BUILD_DIR/output/svc.aerospike.com.key" \
    -password file:"$BUILD_DIR/output/storepass"

    keytool \
    -importkeystore \
    -srckeystore "$BUILD_DIR/output/svc.aerospike.com.p12" \
    -destkeystore "$BUILD_DIR/output/svc.aerospike.com.keystore.jks" \
    -srcstoretype pkcs12 \
    -srcstorepass "$(cat $BUILD_DIR/output/storepass)" \
    -deststorepass "$(cat $BUILD_DIR/output/storepass)" \
    -noprompt

    mv "$BUILD_DIR/output/svc.aerospike.com.keystore.jks" \
    "$BUILD_DIR/certs/svc.aerospike.com.keystore.jks"

    mv "$BUILD_DIR/output/avs.aerospike.com.keystore.jks" \
    "$BUILD_DIR/certs/avs.aerospike.com.keystore.jks"

    mv "$BUILD_DIR/output/ca.aerospike.com.truststore.jks" \
    "$BUILD_DIR/certs/ca.aerospike.com.truststore.jks"

    mv "$BUILD_DIR/output/asd.aerospike.com.pem" \
    "$BUILD_DIR/certs/asd.aerospike.com.pem"

    mv "$BUILD_DIR/output/avs.aerospike.com.pem" \
    "$BUILD_DIR/certs/avs.aerospike.com.pem"

    mv "$BUILD_DIR/output/svc.aerospike.com.pem" \
    "$BUILD_DIR/certs/svc.aerospike.com.pem"

    mv "$BUILD_DIR/output/asd.aerospike.com.key" \
    "$BUILD_DIR/certs/asd.aerospike.com.key"

    mv "$BUILD_DIR/output/ca.aerospike.com.pem" \
    "$BUILD_DIR/certs/ca.aerospike.com.pem"

    mv "$BUILD_DIR/output/keypass" \
    "$BUILD_DIR/certs/keypass"

    mv "$BUILD_DIR/output/storepass" \
    "$BUILD_DIR/certs/storepass"

    echo "Generate Auth Keys"
    openssl genpkey \
    -algorithm RSA \
    -out "$BUILD_DIR/secrets/private_key.pem" \
    -pkeyopt rsa_keygen_bits:2048 \
    -pass "pass:$PASSWORD"

    openssl rsa \
    -pubout \
    -in "$BUILD_DIR/secrets/private_key.pem" \
    -out "$BUILD_DIR/secrets/public_key.pem" \
    -passin "pass:$PASSWORD"
}

# Function to create GKE cluster
create_eks_cluster() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting EKS cluster creation..."
    set -x
    if ! eksctl create cluster \
        --name "$CLUSTER_NAME" \
        --region "$REGION" \
        --profile "$PROFILE" \
        --with-oidc \
        --without-nodegroup \
        --alb-ingress-access \
        --external-dns-access \
        --set-kubeconfig-context; then
        echo "Failed to create EKS cluster"
        exit 1
    else
        echo "EKS cluster created successfully."
    fi

    eksctl create addon --name aws-ebs-csi-driver --cluster "$CLUSTER_NAME" --region "$REGION" --profile "$PROFILE" --force

    echo "Creating Aerospike node pool..."

    if ! eksctl create nodegroup \
        --cluster "$CLUSTER_NAME" \
        --name "$NODE_POOL_NAME_AEROSPIKE" \
        --node-type "m5dn.xlarge" \
        --nodes 3 \
        --nodes-min 3 \
        --nodes-max 3 \
        --region "$REGION" \
        --profile "$PROFILE" \
        --node-volume-size 100 \
        --node-volume-type "gp2" \
        --managed; then
        echo "Failed to create Aerospike node pool"
        exit 1
    else
        echo "Aerospike node pool added successfully."
    fi

    echo "Labeling Aerospike nodes..."
    kubectl get nodes -l eks.amazonaws.com/nodegroup="$NODE_POOL_NAME_AEROSPIKE" -o name | \
        xargs -I {} kubectl label {} aerospike.com/node-pool=default-rack --overwrite

    echo "Adding AVS node pool..."
    if ! eksctl create nodegroup \
        --cluster "$CLUSTER_NAME" \
        --name "$NODE_POOL_NAME_AVS" \
        --node-type "m5dn.xlarge" \
        --nodes 3 \
        --nodes-min 3 \
        --nodes-max 3 \
        --region "$REGION" \
        --profile "$PROFILE" \
        --node-volume-size 100 \
        --node-volume-type "gp2" \
        --managed; then
        echo "Failed to create AVS node pool"
        exit 1
    else
        echo "AVS node pool added successfully."
    fi

    echo "Labeling AVS nodes..."
    kubectl get nodes -l eks.amazonaws.com/nodegroup="$NODE_POOL_NAME_AVS" -o name | \
        xargs -I {} kubectl label {} aerospike.com/node-pool=avs --overwrite
    
    echo "Setting up namespaces..."
    kubectl create namespace aerospike
    kubectl create namespace avs
}

# Function to create Aerospike node pool and deploy AKO
setup_aerospike() {

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
    kubectl --namespace aerospike create serviceaccount aerospike-operator-controller-manager
    kubectl create clusterrolebinding aerospike-cluster \
        --clusterrole=aerospike-cluster --serviceaccount=aerospike:aerospike-operator-controller-manager

    echo "Setting secrets for Aerospike cluster..."
    kubectl --namespace aerospike create secret generic aerospike-secret --from-file="$BUILD_DIR/secrets"
    kubectl --namespace aerospike create secret generic auth-secret --from-literal=password='admin123'
    kubectl --namespace aerospike create secret generic aerospike-tls \
        --from-file="$BUILD_DIR/certs"

    echo "Adding storage class..."
    kubectl apply -f https://raw.githubusercontent.com/aerospike/aerospike-kubernetes-operator/refs/heads/master/config/samples/storage/eks_ssd_storage_class.yaml

    echo "Deploying Aerospike cluster..."
    kubectl apply -f $BUILD_DIR/manifests/aerospike-cr.yaml
}

# Function to setup AVS node pool and namespace
setup_avs() {


    echo "Setting secrets for AVS cluster..."
    kubectl --namespace avs create secret generic auth-secret --from-literal=password='admin123'
    kubectl --namespace avs create secret generic aerospike-tls \
        --from-file="$BUILD_DIR/certs"
    kubectl --namespace avs create secret generic aerospike-secret \
        --from-file="$BUILD_DIR/secrets"
}

# Function to optionally deploy Istio
deploy_istio() {
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
 }

get_reverse_dns() {
    INGRESS_HOSTNAME=$(kubectl get svc istio-ingress -n istio-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    echo "Hostname DNS: $INGRESS_HOSTNAME"
}
# Function to deploy AVS Helm chart
deploy_avs_helm_chart() {
    echo "Deploying AVS Helm chart..."
    helm repo add aerospike-helm https://artifact.aerospike.io/artifactory/api/helm/aerospike-helm
    helm repo update
    if [ -z "$CHART_LOCATION" ]; then
        helm install avs-gke --values $BUILD_DIR/manifests/avs-gke-values.yaml --namespace avs aerospike-helm/aerospike-vector-search --version 0.4.1 --wait
    else
        helm install avs-gke --values $BUILD_DIR/manifests/avs-gke-values.yaml --namespace avs "$CHART_LOCATION" --wait
    fi
}

# Function to setup monitoring
setup_monitoring() {
    echo "Adding monitoring setup..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    helm install monitoring-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

    echo "Applying additional monitoring manifests..."
    kubectl apply -f manifests/monitoring/aerospike-exporter-service.yaml
    kubectl apply -f manifests/monitoring/aerospike-servicemonitor.yaml
    kubectl apply -f manifests/monitoring/avs-servicemonitor.yaml
}

print_final_instructions() {
    
    echo Your new deployment is available at $INGRESS_HOSTNAME.
    echo Check your deployment using our command line tool asvec available at https://github.com/aerospike/asvec.

 
    if [[ "${RUN_INSECURE}" != 1 ]]; then
        echo "connect with asvec using cert "
        cat $BUILD_DIR/certs/ca.aerospike.com.pem
        echo Use the asvec tool to change your password with 
        echo asvec  -h  $INGRESS_HOSTNAME:5000  --tls-cafile path/to/tls/file  -U admin -P admin  user new-password --name admin --new-password your-new-password
    fi


    echo "Setup Complete!"
    
}


#This script runs in this order.
main() {
    set_env_variables
    print_env
    reset_build
    create_eks_cluster
    deploy_istio
    get_reverse_dns
    if [[ "${RUN_INSECURE}" != 1 ]]; then
        generate_certs
    fi
    setup_aerospike
    setup_avs
    deploy_avs_helm_chart
    setup_monitoring
    print_final_instructions
}

# Run the main function
main
