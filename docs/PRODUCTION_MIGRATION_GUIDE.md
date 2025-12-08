# Production Migration Guide

Complete guide for migrating Lodgeick configuration data (Councils, Request Types, and Join DocTypes) to production.

## Prerequisites

- ✅ Lodgeick app installed on production server
- ✅ Database backup completed
- ✅ SSH access to production server
- ✅ Administrator credentials

## 📦 Step 1: Export Data from Development

On your development server, run the export script:

```bash
cd /workspace/development/frappe-bench
bash /tmp/export_lodgeick_data.sh
```

This will create JSON export files in `/tmp/lodgeick_export/`:
- `councils.json` (6 councils)
- `request_types.json` (21 request types)
- `council_landing_pages.json` (6 landing pages)

**Verify export:**
```bash
ls -lh /tmp/lodgeick_export/
```

## 📤 Step 2: Transfer Files to Production

Copy the export directory to your production server:

```bash
# Using scp
scp -r /tmp/lodgeick_export/ user@production-server:/tmp/

# Or using rsync
rsync -avz /tmp/lodgeick_export/ user@production-server:/tmp/lodgeick_export/
```

## 🚀 Step 3: Install DocTypes on Production

First, ensure all DocTypes are installed by running migrations:

```bash
# On production server
cd /path/to/frappe-bench
bench --site your-production-site.com migrate
```

This will install:
- ✅ Login Event DocType (for analytics)
- ✅ Council DocType (if not exists)
- ✅ Request Type DocType (if not exists)
- ✅ Council Landing Page DocType (if not exists)
- ✅ Council Request Type (join table)

## 📥 Step 4: Import Configuration Data

On production server, run the import script:

```bash
cd /path/to/frappe-bench

# Copy import script from development
# Or create it on production using the content below

bash /tmp/import_lodgeick_data.sh your-production-site.com
```

The script will:
1. Import all Councils (or update if they exist)
2. Import all Request Types (or update if they exist)
3. Import all Council Landing Pages (or update if they exist)

## ✅ Step 5: Verify Import

### Check via Desk

```bash
bench browse your-production-site.com
```

Navigate to:
- **Council List**: `/app/council`
- **Request Type List**: `/app/request-type`
- **Council Landing Page List**: `/app/council-landing-page`

### Check via Console

```bash
bench --site your-production-site.com console
```

```python
# Verify councils
councils = frappe.get_all('Council', fields=['name', 'council_code', 'is_active'])
print(f"Total Councils: {len(councils)}")
for c in councils:
    print(f"  - {c.name} ({c.council_code}) - Active: {c.is_active}")

# Verify request types
rts = frappe.get_all('Request Type', fields=['name', 'is_active'])
print(f"\nTotal Request Types: {len(rts)}")

# Verify council-request type links
links = frappe.get_all('Council Request Type', fields=['parent', 'request_type'])
print(f"\nTotal Council-Request Type Links: {len(links)}")
```

## 🎨 Step 6: Rebuild Frontend

```bash
cd /path/to/frappe-bench/apps/lodgeick/frontend
yarn build
```

Or if you want to clear cache and rebuild:

```bash
bench --site your-production-site.com clear-cache
bench build --app lodgeick
```

## 🧪 Step 7: Test Council Landing Pages

Visit these URLs to verify council-specific pages work:

```
https://your-domain.com/frontend/council/AKL
https://your-domain.com/frontend/council/AKL/login
https://your-domain.com/frontend/council/AKL/register
https://your-domain.com/frontend/council/TAYTAY-PH
```

## 🔍 Step 8: Verify Analytics

After a few logins, check Login Event records:

```bash
bench --site your-production-site.com console
```

```python
# Check login events
events = frappe.get_all('Login Event',
    fields=['user', 'source', 'council', 'timestamp'],
    order_by='timestamp desc',
    limit=10
)

for e in events:
    print(f"{e.timestamp} - {e.user} via {e.source} ({e.council or 'N/A'})")
```

## 🛠️ Troubleshooting

### Issue: DocType doesn't exist

**Solution**: Run migrations
```bash
bench --site your-production-site.com migrate
```

### Issue: Permission denied errors

**Solution**: Set Administrator user in import script (already done in script)

### Issue: Import fails for specific records

**Solution**: Check error logs
```bash
bench --site your-production-site.com console
```

```python
# View recent error logs
logs = frappe.get_all('Error Log',
    filters={'creation': ['>', '2025-12-08']},
    fields=['error', 'method'],
    limit=5
)
for log in logs:
    print(f"{log.method}\n{log.error}\n---")
```

### Issue: Council landing pages show 404

**Solution**:
1. Check if frontend is built: `ls -l lodgeick/public/frontend/assets/`
2. Clear cache: `bench --site site.com clear-cache`
3. Restart bench: `bench restart`

## 📋 Export Script Content

If you need to create the export script on a different server:

```bash
#!/bin/bash
cd /workspace/development/frappe-bench
mkdir -p /tmp/lodgeick_export

bench --site lodgeick.localhost console << 'PYTHON'
import frappe
import json

# Export Councils
councils = frappe.get_all('Council', fields=['*'])
council_docs = [frappe.get_doc('Council', c.name).as_dict() for c in councils]
with open('/tmp/lodgeick_export/councils.json', 'w') as f:
    json.dump(council_docs, f, indent=2, default=str)
print(f"✓ Exported {len(council_docs)} councils")

# Export Request Types
rts = frappe.get_all('Request Type', fields=['*'])
rt_docs = [frappe.get_doc('Request Type', rt.name).as_dict() for rt in rts]
with open('/tmp/lodgeick_export/request_types.json', 'w') as f:
    json.dump(rt_docs, f, indent=2, default=str)
print(f"✓ Exported {len(rt_docs)} request types")

# Export Council Landing Pages
lps = frappe.get_all('Council Landing Page', fields=['*'])
lp_docs = [frappe.get_doc('Council Landing Page', lp.name).as_dict() for lp in lps]
with open('/tmp/lodgeick_export/council_landing_pages.json', 'w') as f:
    json.dump(lp_docs, f, indent=2, default=str)
print(f"✓ Exported {len(lp_docs)} landing pages")
PYTHON
```

## 🔄 Alternative: Manual Import via Desk

If scripts don't work, you can manually create records:

1. **Export as CSV**:
   ```bash
   bench --site dev.localhost data-export --doctype="Council"
   ```

2. **Import via UI**:
   - Go to Council List → Menu → Import
   - Upload CSV file
   - Map fields
   - Submit import

## 📊 What Gets Migrated

### Councils (6 records)
- AKL (Auckland Council)
- TAYTAY-PH (Taytay Philippines)
- WLG (Wellington)
- CHC (Christchurch)
- DUD (Dunedin)
- TEST (Test Council)

### Request Types (21 records)
- Building Consents (various types)
- Resource Consents
- LIM Reports
- Code Compliance Certificates
- etc.

### Council Landing Pages (6 records)
- Custom landing pages for each council
- Hero sections, service listings
- Council-specific branding

### Join Tables
- Council Request Type (links councils to their enabled request types)

## 🎯 Summary Checklist

- [ ] Export data from development
- [ ] Transfer files to production
- [ ] Run `bench migrate` on production
- [ ] Import configuration data
- [ ] Verify data in Desk UI
- [ ] Rebuild frontend
- [ ] Test council landing pages
- [ ] Test login flows (system-wide & council-specific)
- [ ] Verify analytics tracking
- [ ] Clear cache and restart

## 📞 Support

If you encounter issues:
1. Check Frappe error logs
2. Review bench console output
3. Verify file permissions
4. Ensure all dependencies installed

---

**Generated by**: Claude Code
**Version**: 1.0
**Last Updated**: 2025-12-08
