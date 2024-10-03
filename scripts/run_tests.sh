#!/bin/env bash

set -eux

COMPOSE="$(command -v docker-compose || echo "$(command -v docker) compose")"

${COMPOSE} -f docker-compose.test.yml build

${COMPOSE} -f docker-compose.test.yml up \
    --abort-on-container-exit \
    --exit-code-from app-test \
    --no-log-prefix \
    --attach app-test

EXIT_CODE=$?