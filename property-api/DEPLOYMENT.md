# Property API Deployment Guide

Complete guide for deploying the Lodgeick Property API (LINZ address search) on a Frappe production server.

## Overview

The Property API is a Node.js Express server that provides LINZ (Land Information New Zealand) address autocomplete and property information lookups. It runs separately from the Frappe backend on port 3000.

## Prerequisites

- Node.js 18.x or higher (already available in Frappe environment)
- Frappe bench setup with lodgeick app installed
- Internet access to LINZ ArcGIS services

## Deployment Methods

Choose one of the following methods based on your server setup:

### Method 1: PM2 (Recommended for Frappe)

PM2 is a production process manager for Node.js applications with built-in load balancing, auto-restart, and monitoring.

#### Step 1: Install PM2 globally

```bash
# As frappe user
npm install -g pm2
```

#### Step 2: Navigate to property-api directory

```bash
cd ~/frappe-bench/apps/lodgeick/property-api
```

#### Step 3: Install dependencies

```bash
npm install
```

#### Step 4: Create PM2 ecosystem file

```bash
cat > ecosystem.config.cjs << 'EOF'
module.exports = {
  apps: [{
    name: 'lodgeick-property-api',
    script: './server.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: '~/.pm2/logs/property-api-error.log',
    out_file: '~/.pm2/logs/property-api-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
}
EOF
```

#### Step 5: Start with PM2

```bash
# Start the service
pm2 start ecosystem.config.cjs

# Save the PM2 process list
pm2 save

# Setup PM2 to start on system boot
pm2 startup
# Follow the instructions shown (you may need to run a command with sudo)
```

#### Step 6: Verify it's running

```bash
# Check status
pm2 status

# View logs
pm2 logs lodgeick-property-api

# Test the API
curl http://localhost:3000/health
curl "http://localhost:3000/api/search?q=123%20Main%20Street"
```

#### PM2 Management Commands

```bash
# Restart the service
pm2 restart lodgeick-property-api

# Stop the service
pm2 stop lodgeick-property-api

# View logs
pm2 logs lodgeick-property-api

# Monitor resources
pm2 monit

# Reload with zero downtime
pm2 reload lodgeick-property-api
```

---

### Method 2: Systemd Service

Use systemd for system-level process management.

#### Step 1: Navigate to property-api directory

```bash
cd ~/frappe-bench/apps/lodgeick/property-api
```

#### Step 2: Install dependencies

```bash
npm install
```

#### Step 3: Create systemd service file

Create `/etc/systemd/system/lodgeick-property-api.service`:

```bash
sudo tee /etc/systemd/system/lodgeick-property-api.service > /dev/null << 'EOF'
[Unit]
Description=Lodgeick Property API - LINZ Address Search
After=network.target

[Service]
Type=simple
User=frappe
WorkingDirectory=/home/frappe/frappe-bench/apps/lodgeick/property-api
ExecStart=/home/frappe/.nvm/versions/node/v20.19.2/bin/node server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lodgeick-property-api

Environment="NODE_ENV=production"
Environment="PORT=3000"

[Install]
WantedBy=multi-user.target
EOF
```

**Note:** Adjust the Node.js path (`/home/frappe/.nvm/versions/node/v20.19.2/bin/node`) to match your installation. Find it with: `which node`

#### Step 4: Enable and start the service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable lodgeick-property-api

# Start the service
sudo systemctl start lodgeick-property-api

# Check status
sudo systemctl status lodgeick-property-api
```

#### Step 5: Verify it's running

```bash
# Check logs
sudo journalctl -u lodgeick-property-api -f

# Test the API
curl http://localhost:3000/health
curl "http://localhost:3000/api/search?q=123%20Main%20Street"
```

#### Systemd Management Commands

```bash
# Restart the service
sudo systemctl restart lodgeick-property-api

# Stop the service
sudo systemctl stop lodgeick-property-api

# Check status
sudo systemctl status lodgeick-property-api

# View logs
sudo journalctl -u lodgeick-property-api -f

# View logs from last hour
sudo journalctl -u lodgeick-property-api --since "1 hour ago"
```

---

### Method 3: Supervisor (Alternative)

If your Frappe installation uses Supervisor (older setups), you can add the property API to Supervisor.

#### Step 1: Create Supervisor config

Create `/etc/supervisor/conf.d/lodgeick-property-api.conf`:

```bash
sudo tee /etc/supervisor/conf.d/lodgeick-property-api.conf > /dev/null << 'EOF'
[program:lodgeick-property-api]
command=/home/frappe/.nvm/versions/node/v20.19.2/bin/node server.js
directory=/home/frappe/frappe-bench/apps/lodgeick/property-api
user=frappe
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/lodgeick-property-api.log
stderr_logfile=/var/log/supervisor/lodgeick-property-api-error.log
environment=NODE_ENV="production",PORT="3000"
EOF
```

#### Step 2: Update Supervisor and start

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lodgeick-property-api
sudo supervisorctl status lodgeick-property-api
```

---

## Nginx Configuration (Recommended)

To allow the frontend to access the API through the same domain (avoiding CORS issues), configure Nginx to proxy requests.

### Step 1: Edit your site's Nginx config

```bash
sudo nano /etc/nginx/sites-available/your-site.conf
```

### Step 2: Add proxy configuration

Add this location block inside your `server` block:

```nginx
server {
    # ... existing configuration ...

    # Property API proxy
    location /property-api/ {
        proxy_pass http://localhost:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # ... rest of configuration ...
}
```

### Step 3: Test and reload Nginx

```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 4: Update frontend API URL

If using Nginx proxy, update your frontend to use `/property-api/` instead of `http://localhost:3000/`:

```javascript
// In NewRequest.vue or wherever the API is called
const PROPERTY_API_URL = window.location.origin + '/property-api/api/search'
```

---

## Monitoring and Troubleshooting

### Check if the service is running

```bash
# PM2
pm2 status

# Systemd
sudo systemctl status lodgeick-property-api

# Supervisor
sudo supervisorctl status lodgeick-property-api

# Check port 3000
sudo lsof -i :3000
# or
sudo netstat -tlnp | grep 3000
```

### View logs

```bash
# PM2
pm2 logs lodgeick-property-api --lines 100

# Systemd
sudo journalctl -u lodgeick-property-api -n 100 -f

# Supervisor
sudo tail -f /var/log/supervisor/lodgeick-property-api.log
```

### Test the API

```bash
# Health check
curl http://localhost:3000/health

# Search test (Lower Hutt)
curl "http://localhost:3000/api/search?q=123%20Main%20Street"

# Via Nginx proxy (if configured)
curl "https://your-domain.com/property-api/health"
curl "https://your-domain.com/property-api/api/search?q=123%20Main%20Street"
```

### Common Issues

#### Issue: Port 3000 already in use

```bash
# Find what's using port 3000
sudo lsof -i :3000

# Kill the process if needed
sudo kill -9 <PID>

# Or change the port in ecosystem.config.js / systemd service
```

#### Issue: "Cannot find module 'express'"

```bash
# Reinstall dependencies
cd ~/frappe-bench/apps/lodgeick/property-api
npm install
```

#### Issue: Permission denied

```bash
# Ensure frappe user owns the directory
sudo chown -R frappe:frappe ~/frappe-bench/apps/lodgeick/property-api
```

#### Issue: API returns CORS errors

- Use Nginx proxy method (recommended)
- Or ensure CORS is properly configured in server.js (already included)

#### Issue: Slow or timing out

- LINZ ArcGIS services may be temporarily slow
- Check server internet connectivity
- Review logs for specific errors

---

## Updates and Maintenance

### Updating the API

When you pull new code changes:

```bash
cd ~/frappe-bench/apps/lodgeick/property-api

# Pull latest changes
git pull

# Install any new dependencies
npm install

# Restart the service
pm2 restart lodgeick-property-api
# or
sudo systemctl restart lodgeick-property-api
```

### Performance Tuning

The API includes:
- **In-memory caching**: 60-second TTL to reduce LINZ API calls
- **Rate limiting**: 120 requests per minute per IP
- **Connection pooling**: Handled by Node.js

For high-traffic sites, consider:
- Increasing instances in PM2 (use CPU cores - 1)
- Adding Redis for distributed caching
- Setting up a CDN for static responses

---

## Security Considerations

1. **Firewall**: Only expose port 3000 to localhost (Nginx proxy should be public-facing)
   ```bash
   sudo ufw allow from 127.0.0.1 to any port 3000
   ```

2. **Rate Limiting**: Already configured (120 req/min per IP)

3. **HTTPS**: Use Nginx with SSL/TLS certificates (Let's Encrypt)

4. **Updates**: Keep Node.js and dependencies updated
   ```bash
   npm audit
   npm audit fix
   ```

---

## Verification Checklist

After deployment, verify:

- [ ] Service is running (`pm2 status` or `systemctl status`)
- [ ] Port 3000 is listening (`sudo lsof -i :3000`)
- [ ] Health endpoint responds (`curl http://localhost:3000/health`)
- [ ] Search returns results (`curl "http://localhost:3000/api/search?q=123"`)
- [ ] Service starts on reboot (test with `sudo reboot`)
- [ ] Logs are accessible and readable
- [ ] Frontend can reach the API (test in browser)
- [ ] Nginx proxy works (if configured)

---

## Support and Resources

- **LINZ Data Service**: https://data.linz.govt.nz/
- **ArcGIS REST API**: https://developers.arcgis.com/rest/
- **PM2 Documentation**: https://pm2.keymetrics.io/
- **Systemd Documentation**: https://www.freedesktop.org/software/systemd/man/

For issues specific to Lodgeick, check the application logs and ensure the LINZ services are accessible from your server.
