# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RequestTypeConditionTemplate(Document):
	"""
	Child table linking Consent Condition Templates to Request Types.
	Defines which conditions apply to which request types.
	"""
	pass
