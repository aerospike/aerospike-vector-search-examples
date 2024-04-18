#!/usr/bin/env bash

# This script automates the creation of Kubernetes ConfigMaps from Grafana dashboard JSON files.
# It is designed to handle both individual JSON files and directories containing JSON files.
# The script recursively searches the given directory for all JSON files, creates a ConfigMap for each,
# labels them for Grafana's sidecar to recognize, and handles names appropriately by sanitizing them
# to meet Kubernetes naming requirements.
#
# Usage:
#   ./create_grafana_dashboards.sh [path to JSON file or directory]
#   If no path is provided, a default path can be set in the script.
#
# The script checks if the input is a directory or a single JSON file:
# - If a directory, it processes all JSON files recursively.
# - If a single JSON file, it processes just that file.
# Each JSON file is used to create a ConfigMap named after the file, sanitized and suffixed with '-dashboard'.
# These ConfigMaps are labeled with 'grafana_dashboard=1' to ensure they are recognized by Grafana's sidecar.
#
# Ensure you have the necessary permissions to execute kubectl commands in your environment.

# Default path for JSON files or directory
DEFAULT_PATH="/path/to/dashboards"

# Use the first script argument as the path, or use the default if no argument provided
INPUT_PATH="${1:-$DEFAULT_PATH}"

# Function to process and create a configmap from a JSON file
process_file() {
    local file="$1"
    local base_name=$(basename "$file" .json)
    local sanitized_name=$(echo "$base_name" | tr '[:upper:]_' '[:lower:]-')

    if [ "${#sanitized_name}" -gt 253 ]; then
        sanitized_name="${sanitized_name:0:253}"
    fi

    kubectl create configmap "${sanitized_name}-dashboard" \
        --from-file="${sanitized_name}.json=$file" \
        -n monitoring \
        --dry-run=client -o yaml | kubectl apply -f - && \
    kubectl label configmap "${sanitized_name}-dashboard" grafana_dashboard=1 -n monitoring --overwrite
}

# Check the type of the input path and process accordingly
if [ -d "$INPUT_PATH" ]; then
    # It's a directory, process all .json files recursively
    find "$INPUT_PATH" -type f -name '*.json' | while read -r file; do
        process_file "$file"
    done
elif [ -f "$INPUT_PATH" ] && [[ "$INPUT_PATH" == *.json ]]; then
    # It's a single file, process it
    process_file "$INPUT_PATH"
else
    echo "The specified path is not valid or does not contain JSON files: $INPUT_PATH"
    exit 1
fi
