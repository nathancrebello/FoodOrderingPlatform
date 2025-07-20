#!/bin/sh
# install_requirements.sh

# Load environment variables from .env.prod
set -a
source .env.prod
set +a

# Check the value of DEBUG and run the appropriate command
if [ "$DEBUG" = "0" ]; then
    poetry export -f requirements.txt --output requirements.txt --without-hashes
    echo "DEBUG is 0"
else
    poetry export -f requirements.txt --output requirements.txt --without-hashes # --with dev
    echo "DEBUG is 1"
fi