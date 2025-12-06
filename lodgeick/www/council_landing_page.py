import frappe
from frappe import _

def get_context(context):
	"""
	Redirect /council/:code to /frontend/council/:code
	This is a server-side redirect that preserves the council code
	and redirects to the Vue SPA frontend.
	"""
	# Extract council code from the URL route parameter
	council_code = frappe.form_dict.get("council_code")

	if not council_code:
		frappe.throw(_("Council code not provided"), frappe.DoesNotExistError)

	council_code = council_code.upper()

	# Verify council exists and is active
	if not frappe.db.exists("Council", council_code):
		frappe.throw(_("Council not found: {0}").format(council_code), frappe.DoesNotExistError)

	council = frappe.get_doc("Council", council_code)
	if not council.is_active:
		frappe.throw(_("Council is not active: {0}").format(council_code), frappe.PermissionError)

	# Redirect to Vue frontend
	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = f"/frontend/council/{council_code.lower()}"
