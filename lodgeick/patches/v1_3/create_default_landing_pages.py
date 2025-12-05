# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe

def execute():
	"""
	Create default Council Landing Pages for all active councils.
	"""
	print("\n" + "="*80)
	print("CREATING DEFAULT COUNCIL LANDING PAGES")
	print("="*80 + "\n")

	councils = frappe.get_all("Council", filters={"is_active": 1}, fields=["council_code", "council_name"])

	created_count = 0
	for council in councils:
		# Check if landing page already exists
		if not frappe.db.exists("Council Landing Page", {"council": council.council_code}):
			try:
				landing_page = frappe.get_doc({
					"doctype": "Council Landing Page",
					"council": council.council_code,
					"is_published": 1,
					"hero_title": f"Welcome to {council.council_name}",
					"hero_subtitle": "Submit planning applications, building consents, and resource consent requests online",
					"primary_cta_text": "Start New Request",
					"primary_cta_link": "/frontend/request/new",
					"show_request_types": 1
				})
				landing_page.insert(ignore_permissions=True)
				print(f"✓ Created landing page for {council.council_code}")
				created_count += 1
			except Exception as e:
				print(f"✗ Failed to create landing page for {council.council_code}: {str(e)}")
		else:
			print(f"- Landing page already exists for {council.council_code}")

	print(f"\n✓ Created {created_count} new council landing pages")
	print("="*80 + "\n")
