#!/bin/bash

# Generate fresh env file from config
bun run export-config.ts > .env

sleep 2
# Run docker compose with generated env file
docker compose --env-file .env up -d
