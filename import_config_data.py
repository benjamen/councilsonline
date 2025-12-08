#!/usr/bin/env python3
"""
Import Councils, Request Types, and related configuration from JSON files
"""

import frappe
import json
import os
import sys

def import_councils(councils_data):
    """Import Council records"""
    count = 0
    for council_data in councils_data:
        try:
            # Check if exists
            if frappe.db.exists('Council', council_data.get('name')):
                print(f"  - Updating Council: {council_data.get('name')}")
                doc = frappe.get_doc('Council', council_data.get('name'))
                doc.update(council_data)
            else:
                print(f"  + Creating Council: {council_data.get('name')}")
                doc = frappe.get_doc(council_data)

            doc.save()
            count += 1
        except Exception as e:
            print(f"  ✗ Error with {council_data.get('name')}: {str(e)}")

    return count

def import_request_types(rt_data):
    """Import Request Type records"""
    count = 0
    for rt in rt_data:
        try:
            # Check if exists
            if frappe.db.exists('Request Type', rt.get('name')):
                print(f"  - Updating Request Type: {rt.get('name')}")
                doc = frappe.get_doc('Request Type', rt.get('name'))
                doc.update(rt)
            else:
                print(f"  + Creating Request Type: {rt.get('name')}")
                doc = frappe.get_doc(rt)

            doc.save()
            count += 1
        except Exception as e:
            print(f"  ✗ Error with {rt.get('name')}: {str(e)}")

    return count

def import_council_landing_pages(lp_data):
    """Import Council Landing Page records"""
    count = 0
    for lp in lp_data:
        try:
            # Check if exists
            if frappe.db.exists('Council Landing Page', lp.get('name')):
                print(f"  - Updating Landing Page: {lp.get('name')}")
                doc = frappe.get_doc('Council Landing Page', lp.get('name'))
                doc.update(lp)
            else:
                print(f"  + Creating Landing Page: {lp.get('name')}")
                doc = frappe.get_doc(lp)

            doc.save()
            count += 1
        except Exception as e:
            print(f"  ✗ Error with {lp.get('name')}: {str(e)}")

    return count

def main(export_dir, site):
    """Import all configuration data"""
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")

    # Import councils
    print("\n📦 Importing Councils...")
    with open(f'{export_dir}/councils.json', 'r') as f:
        councils = json.load(f)
    count = import_councils(councils)
    print(f"  ✓ Imported {count} councils")

    # Import request types
    print("\n📦 Importing Request Types...")
    with open(f'{export_dir}/request_types.json', 'r') as f:
        request_types = json.load(f)
    count = import_request_types(request_types)
    print(f"  ✓ Imported {count} request types")

    # Import landing pages
    print("\n📦 Importing Council Landing Pages...")
    with open(f'{export_dir}/council_landing_pages.json', 'r') as f:
        landing_pages = json.load(f)
    count = import_council_landing_pages(landing_pages)
    print(f"  ✓ Imported {count} landing pages")

    frappe.db.commit()
    print("\n✅ Import complete!")

    frappe.destroy()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 import_config_data.py <export_dir> <site>")
        print("Example: python3 import_config_data.py /tmp/lodgeick_export production.localhost")
        sys.exit(1)

    export_dir = sys.argv[1]
    site = sys.argv[2]
    main(export_dir, site)
