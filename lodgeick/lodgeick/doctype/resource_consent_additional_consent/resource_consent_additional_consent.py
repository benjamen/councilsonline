# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResourceConsentAdditionalConsent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		consent_status: DF.Literal["Required", "Applied", "Granted", "Declined"] | None
		consent_type: DF.Literal["Discharge Permit", "Coastal Permit", "Water Permit", "NES Soils", "Other"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_number: DF.Data | None
	# end: auto-generated types

	pass
