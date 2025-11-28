#!/usr/bin/env python3
import frappe
from frappe.utils import flt
from lodgeick.custom_fields import create_lodgeick_custom_fields

if __name__ == "__main__":
	import sys
	site = sys.argv[1] if len(sys.argv) > 1 else "hohmesy.com"
	frappe.init(site=site)
	frappe.connect()

	print(f"Creating custom fields for site: {site}")
	create_lodgeick_custom_fields()
	print("✓ Custom fields created successfully!")
