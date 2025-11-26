#!/bin/bash
# Startup script for Lodgeick Property API

cd "$(dirname "$0")"

echo "Starting Lodgeick Property API..."
echo "Server will be available at http://localhost:3000"
echo ""
echo "API Endpoints:"
echo "  - GET /api/search?q=<address>  (Search for properties)"
echo "  - GET /health                   (Health check)"
echo ""

node server.js
