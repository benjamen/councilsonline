# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RCConsentType(Document):
	"""Child table for storing Resource Consent types with descriptions."""

	def before_save(self):
		"""Auto-fill description based on consent type selection."""
		descriptions = {
			"Land Use": "For buildings, structures, and use of land",
			"Subdivision": "For dividing land into separate lots or titles",
			"Discharge Permit": "For stormwater, wastewater, or air discharges",
			"Water Permit": "For taking, using, damming, or diverting water",
			"Coastal Permit": "For structures or activities in the coastal marine area"
		}

		if self.consent_type in descriptions:
			self.description = descriptions[self.consent_type]
