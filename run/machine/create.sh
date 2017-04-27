#!/usr/bin/env bash

set -e

manager_count=2
worker_count=3

docker-machine create \
  --driver "virtualbox" \
  --virtualbox-disk-size "5000" \
  registry

registry_ip=$(docker-machine ip registry)

for node_type in manager worker; do
  count_var=${node_type}_count
  for (( i=0; i<${!count_var}; ++i )); do
    docker-machine create \
      --driver "virtualbox" \
      --engine-opt "experimental=true" \
      --virtualbox-disk-size "5000" \
      --engine-insecure-registry "${registry_ip}:5000" \
      "${node_type}${i}"
  done
done

swarm_ip=$(docker-machine ip manager0)

declare -a tokens
tokens=($(
  eval $(docker-machine env manager0)
  docker swarm init --advertise-addr ${swarm_ip} > /dev/null
  docker swarm join-token --quiet manager
  docker swarm join-token --quiet worker
))

manager_token=${tokens[0]}
worker_token=${tokens[1]}

echo "manager: ${manager_token}, worker: ${worker_token}"

(
  eval $(docker-machine env registry)
  docker-compose up -d
)

echo "Running registry on ${registry_ip}:5000"

manager_start=1
worker_start=0
for node_type in manager worker; do
  start_var=${node_type}_start
  count_var=${node_type}_count
  token_var=${node_type}_token
  for (( i=${!start_var}; i<${!count_var}; ++i )); do
    machine_name=${node_type}${i}
    (
      echo "Join swarm ${swarm_ip} with ${machine_name}"
      eval $(docker-machine env ${machine_name})
      docker swarm join --token ${!token_var} ${swarm_ip}
    )
  done
done
