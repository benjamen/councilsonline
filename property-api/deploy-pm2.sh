#!/bin/bash
# Quick deployment script for Lodgeick Property API using PM2
# Usage: ./deploy-pm2.sh

set -e

echo "=========================================="
echo "Lodgeick Property API - PM2 Deployment"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "server.js" ]; then
    echo "Error: server.js not found. Please run this script from the property-api directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo ""
    echo "⚠️  PM2 is not installed globally."
    echo "Install it with: npm install -g pm2"
    echo ""
    read -p "Would you like to install PM2 now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install -g pm2
    else
        echo "Deployment cancelled. Please install PM2 and try again."
        exit 1
    fi
fi

# Stop existing instance if running
echo ""
echo "🛑 Stopping existing instance (if any)..."
pm2 delete lodgeick-property-api 2>/dev/null || true

# Start with PM2
echo ""
echo "🚀 Starting with PM2..."
pm2 start ecosystem.config.js

# Save PM2 process list
echo ""
echo "💾 Saving PM2 process list..."
pm2 save

# Setup PM2 startup
echo ""
echo "⚙️  Setting up PM2 startup script..."
echo "Note: You may need to run the command shown below with sudo"
pm2 startup

# Show status
echo ""
echo "✅ Deployment complete!"
echo ""
pm2 status

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. If PM2 showed a startup command above, run it with sudo"
echo "2. Test the API:"
echo "   curl http://localhost:3000/health"
echo ""
echo "3. View logs:"
echo "   pm2 logs lodgeick-property-api"
echo ""
echo "4. Configure Nginx proxy (optional but recommended):"
echo "   See nginx-proxy.conf for configuration"
echo ""
echo "=========================================="
