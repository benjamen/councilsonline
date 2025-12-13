# Socket.io Setup Guide

## Overview
Socket.io provides realtime features for Frappe/ERPNext applications. This guide explains how to enable and troubleshoot Socket.io.

## Bug 2: Socket.io Connection Failure

### Root Cause
Socket.io is configured in supervisor but not running. This is an **operational fix**, not a code fix.

### Solution Options

#### Option 1: Start via Supervisor (Recommended for Production)

Socket.io is already configured in `/workspace/development/frappe-bench/config/supervisor.conf` as `frappe-bench-node-socketio`.

**Start Socket.io:**
```bash
cd /workspace/development/frappe-bench
supervisorctl restart frappe-bench-node-socketio

# Or restart all services
bench restart
```

**Verify it's running:**
```bash
supervisorctl status frappe-bench-node-socketio

# Should show:
# frappe-bench-node-socketio   RUNNING   pid 12345, uptime 0:00:05
```

**Check logs:**
```bash
tail -f logs/node-socketio.log
tail -f logs/node-socketio.error.log
```

#### Option 2: Manual Start (Development Only)

For development/testing, use the provided script:

```bash
cd /workspace/development
./start-socketio.sh
```

**Note**: This keeps Socket.io in the foreground. Press Ctrl+C to stop.

#### Option 3: Background Process (Development Alternative)

```bash
cd /workspace/development/frappe-bench
nohup node apps/frappe/socketio.js > logs/socketio.log 2>&1 &
echo $! > logs/socketio.pid

# To stop:
kill $(cat logs/socketio.pid)
```

## Configuration

Socket.io port is configured in `sites/common_site_config.json`:

```json
{
  "socketio_port": 9000
}
```

## Nginx Configuration

Ensure nginx is proxying WebSocket connections:

```nginx
location /socket.io {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header X-Frappe-Site-Name $host;
    proxy_set_header Origin $scheme://$http_host;
    proxy_set_header Host $host;

    proxy_pass http://127.0.0.1:9000/socket.io;
}
```

## Testing Socket.io

### Browser Console Test

```javascript
// Open browser console on your Frappe site
frappe.socketio.socket.connected
// Should return: true

// Listen for events
frappe.socketio.on('msgprint', (data) => {
    console.log('Socket.io message:', data);
});
```

### Command Line Test

```bash
# Check if port 9000 is listening
netstat -tlnp | grep 9000
# OR
ss -tlnp | grep 9000

# Test connection
curl http://localhost:9000/socket.io/
# Should return: 0 (this is expected - Socket.io handshake)
```

## Troubleshooting

### Socket.io Not Starting

1. **Check Node.js version:**
   ```bash
   node --version
   # Should be v14+ (v20.19.2 in this environment)
   ```

2. **Check if port 9000 is already in use:**
   ```bash
   lsof -i :9000
   # If occupied, either kill the process or change socketio_port
   ```

3. **Check supervisor logs:**
   ```bash
   tail -50 /workspace/development/frappe-bench/logs/node-socketio.error.log
   ```

4. **Verify socketio.js exists:**
   ```bash
   ls -l /workspace/development/frappe-bench/apps/frappe/socketio.js
   ```

### Connection Refused in Browser

1. **Verify Socket.io is running** (see above)

2. **Check nginx configuration:**
   ```bash
   nginx -t
   # Should show: syntax is ok
   ```

3. **Reload nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

4. **Check browser console** for WebSocket errors

### Performance Issues

1. **Check Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Monitor Socket.io logs:**
   ```bash
   tail -f /workspace/development/frappe-bench/logs/node-socketio.log
   ```

3. **Check system resources:**
   ```bash
   top
   # Check CPU and memory usage
   ```

## Production Deployment

For production (on lodgeick.com), Socket.io should be managed by supervisor:

```bash
# On production server
cd /home/frappe-user/frappe-bench

# Start all services including Socket.io
sudo supervisorctl start all

# Or just Socket.io
sudo supervisorctl start frappe-bench-node-socketio

# Check status
sudo supervisorctl status
```

## Integration with deploy.yml

The deployment workflow automatically restarts all supervisor processes, including Socket.io:

```yaml
# In .github/workflows/deploy.yml
- name: Restart bench services
  run: |
    sudo supervisorctl stop all
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start all
```

## Summary

**Bug 2 Fix**: Operational - Not a code issue. Socket.io is already configured and just needs to be started via supervisor.

**Action Required**:
- Development: Run `supervisorctl restart frappe-bench-node-socketio`
- Production: Automatically handled by deploy.yml (no code changes needed)

**Status**: ✅ Socket.io is configured and ready to use - just needs to be started
