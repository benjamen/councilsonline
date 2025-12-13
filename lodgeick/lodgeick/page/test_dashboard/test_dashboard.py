import frappe

def get_context(context):
	context.no_cache = 1

	# Only allow System Managers
	if not frappe.has_permission("Test Runner", "read"):
		frappe.throw("Not permitted", frappe.PermissionError)

	return context
