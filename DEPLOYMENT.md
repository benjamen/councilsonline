# Lodgeick Deployment Guide

## Overview

This document describes the GitHub Actions deployment workflow for Lodgeick to the production server.

## Deployment Architecture

- **Repository**: https://github.com/benjamen/lodgeick.git
- **Production Server**: 77.37.87.141
- **Site URL**: https://lodgeick.com
- **Server User**: root (switches to frappe-user)
- **Bench Path**: /home/frappe-user/frappe-bench

## Automated Deployment

### Trigger Methods

1. **Automatic**: Push to `main` branch
2. **Manual**: Use GitHub Actions "Run workflow" button

### Deployment Process

The workflow performs the following steps:

1. **Pull Latest Code**
   - Fetches and resets to `origin/main`
   - Cleans untracked files

2. **Install Dependencies**
   - Runs `yarn install` in frontend directory
   - Uses frozen lockfile when possible

3. **Build Frontend**
   - Compiles Vue.js application
   - Generates production assets

4. **Build Backend Assets**
   - Runs `bench build --app lodgeick`
   - Compiles Python and JavaScript assets

5. **Run Migrations**
   - Applies database schema changes
   - Non-blocking if migrations fail

6. **Clear Cache**
   - Clears application cache
   - Clears website cache

7. **Restart Services**
   - Restarts Frappe bench services
   - Ensures new code is loaded

8. **Verify Deployment**
   - Checks if site returns HTTP 200/302
   - Reports deployment status

## Prerequisites

### Required GitHub Secrets

Configure these in: `Settings > Secrets and variables > Actions`

1. **SSH_PRIVATE_KEY**
   - Private SSH key for root@77.37.87.141
   - Must have passwordless access
   - Should be Ed25519 or RSA key

### Server Requirements

1. **SSH Access**
   ```bash
   ssh root@77.37.87.141
   ```

2. **Sudo Access for frappe-user**
   ```bash
   # /etc/sudoers.d/frappe-user
   root ALL=(frappe-user) NOPASSWD: /bin/bash
   ```

3. **Git Configuration**
   ```bash
   # On server as frappe-user
   cd /home/frappe-user/frappe-bench/apps/lodgeick
   git config --global --add safe.directory /home/frappe-user/frappe-bench/apps/lodgeick
   ```

4. **SSH Key for GitHub**
   - frappe-user should have SSH key added to GitHub
   - Or use HTTPS with token

## Configuration

### Environment Variables

Edit `.github/workflows/deploy.yml`:

```yaml
env:
  SERVER_HOST: 77.37.87.141      # Production server IP
  SERVER_USER: root               # SSH user
  BENCH_PATH: /home/frappe-user/frappe-bench
  SITE_NAME: lodgeick.com        # Frappe site name
  APP_NAME: lodgeick             # App directory name
```

### GitHub Environment

The workflow uses the `production` environment. Configure in:
`Settings > Environments > production`

**Recommended Settings:**
- Required reviewers: Add team members
- Deployment branches: `main` only
- Environment secrets: SSH_PRIVATE_KEY

## Manual Deployment

### From Local Machine

```bash
# SSH into server
ssh root@77.37.87.141

# Switch to frappe user
sudo -u frappe-user bash

# Navigate to bench
cd /home/frappe-user/frappe-bench

# Pull latest code
cd apps/lodgeick
git pull origin main

# Build frontend
cd frontend
yarn install
yarn build

# Build backend and migrate
cd /home/frappe-user/frappe-bench
bench build --app lodgeick
bench --site lodgeick.com migrate
bench --site lodgeick.com clear-cache
bench restart
```

### From GitHub Actions

1. Go to: `Actions > Deploy to Production`
2. Click: `Run workflow`
3. Select branch: `main`
4. Click: `Run workflow`

## Troubleshooting

### Common Issues

#### 1. SSH Connection Failed
```
Error: Permission denied (publickey)
```

**Solution:**
- Verify SSH_PRIVATE_KEY secret is correct
- Check key format (should start with `-----BEGIN OPENSSH PRIVATE KEY-----`)
- Ensure server allows key-based authentication

#### 2. Git Pull Failed
```
Error: fatal: could not read Username for 'https://github.com'
```

**Solution:**
- Ensure frappe-user has SSH access to GitHub
- Add SSH key to GitHub: `cat ~/.ssh/id_ed25519.pub`
- Or configure git with token

#### 3. Permission Denied
```
Error: Permission denied
```

**Solution:**
- Check sudo configuration for frappe-user
- Verify file permissions in bench directory

#### 4. Build Failed
```
Error: yarn build failed
```

**Solution:**
- SSH into server and check logs
- Ensure Node.js and Yarn are installed
- Check for syntax errors in Vue files

#### 5. Migration Failed
```
Error: bench --site lodgeick.com migrate failed
```

**Solution:**
- Check database connectivity
- Review migration logs: `bench --site lodgeick.com console`
- Migrations are non-blocking, check if app still works

#### 6. Site Not Accessible
```
Error: Site returned HTTP 000 or 500
```

**Solution:**
- Check if bench is running: `supervisorctl status all`
- Review error logs: `tail -f /home/frappe-user/frappe-bench/logs/*.log`
- Restart manually: `bench restart`

## Monitoring

### View Deployment Logs

1. **GitHub Actions Logs**
   - Go to: `Actions > Deploy to Production`
   - Click on latest run
   - View detailed logs for each step

2. **Server Logs**
   ```bash
   # Frappe logs
   tail -f /home/frappe-user/frappe-bench/logs/web.log
   tail -f /home/frappe-user/frappe-bench/logs/worker.log

   # Supervisor logs
   sudo tail -f /var/log/supervisor/supervisord.log
   ```

3. **Bench Status**
   ```bash
   sudo -u frappe-user bash
   cd /home/frappe-user/frappe-bench
   bench doctor
   ```

### Rollback Procedure

If deployment fails:

```bash
# SSH into server
ssh root@77.37.87.141
sudo -u frappe-user bash
cd /home/frappe-user/frappe-bench/apps/lodgeick

# View recent commits
git log --oneline -10

# Rollback to previous commit
git reset --hard <previous-commit-hash>

# Rebuild and restart
cd /home/frappe-user/frappe-bench
bench build --app lodgeick
bench --site lodgeick.com clear-cache
bench restart
```

## Security Best Practices

1. **SSH Keys**
   - Use Ed25519 keys (more secure than RSA)
   - Never commit private keys to repository
   - Rotate keys periodically

2. **GitHub Secrets**
   - Limit access to repository secrets
   - Use environment protection rules
   - Enable audit logs

3. **Server Security**
   - Keep server updated: `sudo apt update && sudo apt upgrade`
   - Use firewall: `sudo ufw status`
   - Monitor SSH access: `sudo tail -f /var/log/auth.log`

4. **Least Privilege**
   - frappe-user should not have root access
   - Use sudo only for specific commands
   - Regularly review permissions

## Performance Optimization

1. **Build Caching**
   - Yarn cache is preserved between builds
   - Consider adding bench build cache

2. **Zero Downtime**
   - Consider blue-green deployment
   - Use `bench --site lodgeick.com set-maintenance-mode on/off`

3. **CDN Integration**
   - Serve static assets via CDN
   - Configure in `site_config.json`

## Support

For deployment issues:

1. Check GitHub Actions logs
2. Review server logs
3. Test manual deployment steps
4. Contact DevOps team

## Changelog

- **2025-01-20**: Improved deployment workflow with heredoc SSH commands
- **2025-01-20**: Added environment variables for easy configuration
- **2025-01-20**: Added deployment summary and verification steps
- **2025-01-20**: Switched to root user with sudo to frappe-user
