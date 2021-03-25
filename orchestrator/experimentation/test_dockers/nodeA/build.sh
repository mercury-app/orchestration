#!/bin/bash

docker_name=$(basename $PWD)
docker_name=$(echo "${docker_name,,}")
echo "docker name: "$docker_name

docker build -t $docker_name .
