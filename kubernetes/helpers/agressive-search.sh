#!/bin/bash

usage() {
    echo "Usage: $0 [host]"
    echo "host: The URL of the host to send requests to. example: $0 http://35.226.165.134:8080/rest/v1/search"
}


# Define how many requests you want to send
total_requests=1000

# Check if host argument is provided, otherwise use default
if [ -z "$1" ]; then
    usage
else
    host="$1"
fi


# Check if help argument is provided
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage
    exit 0
fi

for i in $(seq 1 $total_requests); do
        # Generate a random word using /dev/urandom
        random_word=$(tr -dc 'a-z' </dev/urandom | head -c $((RANDOM % 10 + 3))) # words of length 3-12

        curl "$host" \
            -X POST \
            -H 'Content-Type: multipart/form-data; boundary=---------------------------35049604720377388463476083706' \
            --data-binary $'-----------------------------35049604720377388463476083706\r\nContent-Disposition: form-data; name="text"\r\n\r\n'"$random_word"$'\r\n-----------------------------35049604720377388463476083706--\r\n' | jq\
            & # Run in background for concurrency
done

wait # Wait for all background jobs to finish