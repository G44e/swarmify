#!/bin/bash

set -e

echo "Running as $(id)"

# Allow the container to be started with `--user`
if [ "$1" = 'storm' -a "$(id -u)" = '0' ]; then
    chown -R "$STORM_USER" "$STORM_DATA_DIR" "$STORM_DATA_LOG_DIR" "$STORM_CONF_DIR"
    exec su-exec "$STORM_USER" "$0" "$@"
fi

# Generate the config only if it doesn't exist
#if [ ! -f "$STORM_CONF_DIR/storm.yaml" ]; then
if [ "$1" = 'storm' ]; then
  create_config.py
fi

exec "$@"
