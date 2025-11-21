# Copyright (c) 2025, Optified and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssessmentStageType(Document):
	"""
	Master data for assessment stage types.

	Defines reusable stage types like:
	- Vetting (S88 completeness, AEE validation)
	- Technical Assessment (S95/S104 analysis, effects assessment)
	- Decision (S108AA conditions, decision notification)
	- Implementation (Consent issue, S223/224c, DC)

	Each stage type can have custom field definitions stored as JSON schema
	to validate stage_data fields in Assessment Stage Instance.
	"""
	pass
