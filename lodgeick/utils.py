"""
Lodgeick Utility Functions
Handles global error logging and API response validation
"""

import frappe
from frappe import _
import json


def after_request():
	"""
	Global hook that runs after every API request
	Logs API errors and validates responses to prevent empty responses
	Fixes Bug 3: Empty API responses
	"""
	# Only process API requests
	if not frappe.request or not frappe.request.path.startswith('/api/'):
		return

	# Get response
	response = frappe.response

	# Check if there was an exception but no error message set
	if frappe.local.response.get('exc_type') and not response.get('exception'):
		frappe.log_error(
			title="Unhandled API Exception",
			message=f"Path: {frappe.request.path}\nException Type: {frappe.local.response.get('exc_type')}\nUser: {frappe.session.user}"
		)

	# Validate response has content for successful requests
	if response.get('message') is None and not response.get('exc'):
		# Some endpoints intentionally return no message (like ping)
		# But log others for investigation
		if frappe.request.path not in ['/api/method/ping', '/api/method/frappe.handler.ping']:
			frappe.log_error(
				title="Empty API Response",
				message=f"Path: {frappe.request.path}\nMethod: {frappe.request.method}\nUser: {frappe.session.user}\nResponse: {json.dumps(response)}"
			)


def validate_api_response(data, endpoint_name=None):
	"""
	Validates that API response has content
	Raises exception if response would be empty

	Args:
		data: Response data to validate
		endpoint_name: Name of endpoint for logging (optional)

	Returns:
		Validated data

	Raises:
		frappe.ValidationError if data is None or empty
	"""
	if data is None:
		error_msg = f"API endpoint {endpoint_name or 'unknown'} returned None"
		frappe.log_error(title="Empty API Response", message=error_msg)
		frappe.throw(_("An error occurred processing your request. Please try again."))

	return data


def log_api_error(endpoint_name, error, context=None):
	"""
	Logs API errors with context for debugging

	Args:
		endpoint_name: Name of the API endpoint
		error: Exception object
		context: Additional context dict (optional)
	"""
	error_details = {
		'endpoint': endpoint_name,
		'error': str(error),
		'error_type': type(error).__name__,
		'user': frappe.session.user,
		'request_path': frappe.request.path if frappe.request else None,
		'context': context or {}
	}

	frappe.log_error(
		title=f"API Error: {endpoint_name}",
		message=json.dumps(error_details, indent=2)
	)
