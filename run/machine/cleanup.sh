#!/usr/bin/env bash

docker-machine rm --force $(docker-machine ls --quiet)
