#!/usr/bin/env bash

# Default directory containing the JSON files
DEFAULT_DIR="/path/to/dashboards"

# Use the first script argument as the directory, or use the default if no argument provided
DASHBOARD_DIR="${1:-$DEFAULT_DIR}"

# Check if the specified directory exists
if [ ! -d "$DASHBOARD_DIR" ]; then
    echo "The specified directory does not exist: $DASHBOARD_DIR"
    exit 1
fi

# Loop over each JSON file in the directory
for file in "$DASHBOARD_DIR"/*.json; do
    # Extract the base filename without the extension
    base_name=$(basename "$file" .json)
    # Create a ConfigMap with a unique name and key based on the original file name
    kubectl create configmap "${base_name}-dashboard" \
        --from-file="${base_name}.json=$file" \
        -n monitoring \
        --dry-run=client -o yaml | kubectl apply -f -
done
