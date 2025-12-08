#!/usr/bin/env python3
"""
Export Councils, Request Types, and related configuration to JSON files
for migration to production
"""

import frappe
import json
import os
from frappe.utils import now

def export_councils():
    """Export all Council records"""
    councils = frappe.get_all('Council', fields=['*'])

    council_docs = []
    for council in councils:
        doc = frappe.get_doc('Council', council.name)
        council_docs.append(doc.as_dict())

    return council_docs

def export_request_types():
    """Export all Request Type records"""
    request_types = frappe.get_all('Request Type', fields=['*'])

    rt_docs = []
    for rt in request_types:
        doc = frappe.get_doc('Request Type', rt.name)
        rt_docs.append(doc.as_dict())

    return rt_docs

def export_council_request_types():
    """Export all Council Request Type links"""
    links = frappe.get_all('Council Request Type', fields=['*'])
    return links

def export_council_landing_pages():
    """Export all Council Landing Page records"""
    landing_pages = frappe.get_all('Council Landing Page', fields=['*'])

    lp_docs = []
    for lp in landing_pages:
        doc = frappe.get_doc('Council Landing Page', lp.name)
        lp_docs.append(doc.as_dict())

    return lp_docs

def main():
    """Export all configuration data"""
    frappe.init(site='lodgeick.localhost')
    frappe.connect()

    export_dir = '/tmp/lodgeick_export'
    os.makedirs(export_dir, exist_ok=True)

    # Export councils
    print("Exporting Councils...")
    councils = export_councils()
    with open(f'{export_dir}/councils.json', 'w') as f:
        json.dump(councils, f, indent=2, default=str)
    print(f"  ✓ Exported {len(councils)} councils")

    # Export request types
    print("Exporting Request Types...")
    request_types = export_request_types()
    with open(f'{export_dir}/request_types.json', 'w') as f:
        json.dump(request_types, f, indent=2, default=str)
    print(f"  ✓ Exported {len(request_types)} request types")

    # Export council request type links
    print("Exporting Council Request Type links...")
    links = export_council_request_types()
    with open(f'{export_dir}/council_request_type_links.json', 'w') as f:
        json.dump(links, f, indent=2, default=str)
    print(f"  ✓ Exported {len(links)} links")

    # Export landing pages
    print("Exporting Council Landing Pages...")
    landing_pages = export_council_landing_pages()
    with open(f'{export_dir}/council_landing_pages.json', 'w') as f:
        json.dump(landing_pages, f, indent=2, default=str)
    print(f"  ✓ Exported {len(landing_pages)} landing pages")

    print(f"\n✅ Export complete! Files saved to: {export_dir}")
    print("\nTo import on production:")
    print("1. Copy the JSON files to your production server")
    print("2. Run: bench --site your-site.com import-config-data /path/to/export/dir")

    frappe.destroy()

if __name__ == '__main__':
    main()
