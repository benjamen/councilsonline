# Property API - Quick Start Guide

**5-Minute Setup** for deploying the LINZ address search API on your Frappe production server.

## Fastest Method: PM2 (Recommended)

### 1. SSH into your production server

```bash
ssh your-server
```

### 2. Navigate to the property-api directory

```bash
cd ~/frappe-bench/apps/lodgeick/property-api
```

### 3. Run the automated deployment script

```bash
./deploy-pm2.sh
```

This script will:
- Install npm dependencies
- Install PM2 if needed
- Start the API service
- Configure auto-restart on failure
- Set up boot startup

### 4. Follow the post-deployment instructions

If PM2 shows a startup command, run it (example):

```bash
sudo env PATH=$PATH:/home/frappe/.nvm/versions/node/v20.19.2/bin pm2 startup systemd -u frappe --hp /home/frappe
```

### 5. Test it works

```bash
# Health check
curl http://localhost:3000/health

# Search test
curl "http://localhost:3000/api/search?q=123%20Main%20Street"
```

### 6. Configure Nginx (Optional but Recommended)

Add this to your Frappe site's Nginx config (`/etc/nginx/sites-available/your-site.conf`):

```nginx
# Property API proxy
location /property-api/ {
    proxy_pass http://localhost:3000/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Then reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Done!

Your Property API is now running and will:
- ✅ Start automatically on server boot
- ✅ Restart automatically if it crashes
- ✅ Log all activity to PM2 logs

## Common Commands

```bash
# View status
pm2 status

# View logs
pm2 logs lodgeick-property-api

# Restart
pm2 restart lodgeick-property-api

# Stop
pm2 stop lodgeick-property-api

# Monitor resources
pm2 monit
```

## Need More Details?

See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Alternative deployment methods (systemd, supervisor)
- Detailed Nginx configuration
- Troubleshooting guide
- Security best practices
- Performance tuning

## Troubleshooting

**API not responding?**
```bash
pm2 logs lodgeick-property-api --lines 50
```

**Port 3000 already in use?**
```bash
sudo lsof -i :3000
# Kill the process or change PORT in ecosystem.config.js
```

**Frontend can't reach API?**
- Configure Nginx proxy (step 6 above)
- Or update frontend to use `http://your-domain.com:3000`
- Check firewall rules allow port 3000

## Support

For detailed deployment instructions and troubleshooting, see [DEPLOYMENT.md](./DEPLOYMENT.md).
