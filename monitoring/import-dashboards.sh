#!/usr/bin/env bash

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
