#!/bin/bash
set -e
# make sure to call this script from the make file only
DOCKER_IMAGE="azemataya/some-repo"
docker build -t $DOCKER_IMAGE -f ./.docker/prod.Dockerfile .
docker push $DOCKER_IMAGE
