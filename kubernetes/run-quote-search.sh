#!/bin/bash -e
WORKSPACE=/tmp #"$(git rev-parse --show-toplevel)"
PROJECT="aerostation-dev"
ZONE="us-central1-c"

gcloud compute instances create proximus-app \
--zone="$ZONE" \
--machine-type=e2-medium \
--boot-disk-size=200GB \
--image-project=ubuntu-os-cloud \
--image-family=ubuntu-2310-amd64 \
--metadata=startup-script="$(cat <<-EOF
#!/bin/bash -e
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm -f get-docker.sh
EOF
)"
sleep 2m

gcloud compute ssh proximus-app \
--zone="$ZONE" \
--project="$PROJECT" \
--command="sudo usermod -aG docker $USER"
mkdir -p "$WORKSPACE/aerospike-proximus/gke"
cat <<-EOF > "$WORKSPACE/aerospike-proximus/gke/build-app.sh"
#!/bin/bash -e
git clone  https://github.com/aerospike/proximus-examples.git
cd ./proximus-examples/quote-semantic-search
docker build -f "Dockerfile-quote-search" -t "quote-search" .
cd -
rm -rf ./proximus-examples
EOF
chmod +x "$WORKSPACE/aerospike-proximus/gke/build-app.sh"

gcloud compute scp $WORKSPACE/aerospike-proximus/gke/build-app.sh proximus-app:~/build-app.sh \
--zone="$ZONE" \
--project="$PROJECT"
rm "$WORKSPACE/aerospike-proximus/gke/build-app.sh"

gcloud compute ssh proximus-app --zone="$ZONE" --project="$PROJECT" -- "./build-app.sh"

cat <<-EOF > "$WORKSPACE/aerospike-proximus/gke/run-app.sh"
#!/bin/bash -e
mkdir -p ./data
curl -L -o "./data/quotes.csv.tgz" \
https://github.com/aerospike/proximus-examples/raw/main/quote-semantic-search/container-volumes/quote-search/data/quotes.csv.tgz
docker run -d \
--name "quote-search" \
-v "./data:/container-volumes/quote-search/data" \
-p "8080:8080" \
-e "PROXIMUS_HOST=$(kubectl -n aerospike get svc/proximus-gke-aerospike-proximus-lb \
-o=jsonpath='{.status.loadBalancer.ingress[0].ip}')" \
-e "PROXIMUS_PORT=5000" \
-e "APP_NUM_QUOTES=5000" \
-e "GRPC_DNS_RESOLVER=native" \
-e "PROXIMUS_IS_LOADBALANCER=True" quote-search
EOF

chmod +x "$WORKSPACE/aerospike-proximus/gke/run-app.sh"

gcloud compute scp $WORKSPACE/aerospike-proximus/gke/run-app.sh proximus-app:~/run-app.sh \
--zone="$ZONE" \
--project="$PROJECT"
rm "$WORKSPACE/aerospike-proximus/gke/run-app.sh"

gcloud compute ssh proximus-app --zone="$ZONE" --project="$PROJECT" -- "./run-app.sh"

echo "to expose your web app to the world, run the following commands adapted to your enviroment"
echo 'gcloud compute firewall-rules create allow-8080 --network default --allow tcp:8080 --target-tags http-server --direction INGRESS'
echo 'gcloud compute instances add-tags proximus-app --tags http-server --zone us-central1-c'