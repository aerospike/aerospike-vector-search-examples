# Metrics Collecting

In the `docker-compose.yaml` file, metrics collection is configured to monitor the performance and health of the Aerospike Vector Search example docker compose.

## DISCLOSURE
This docker file is included by default in the docker compose in the /docker directory.
It collected basic usage and reports it to a central Aerospike server so we can better understand Aerospike Vector Search usage.

### Usage
To use this compose file simply include it in your docker compose
It requires
- That a service for AVS called `aerospike-vector-search` is defined and that AVS's prometheus metrics service is exposed on port 5040.
- Access to the internet.
