#!/bin/bash
docker compose down --remove-orphans
docker compose build

# Start Docker Compose
docker compose up -d

# Wait for the `omopcodegen` container to finish
#docker wait $(docker compose ps -q omopcodegen)
docker compose logs -f omopcodegen
# Stop the `postgresql` container
docker compose down