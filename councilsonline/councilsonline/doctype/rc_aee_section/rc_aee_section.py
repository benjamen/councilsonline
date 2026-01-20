# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RCAEESection(Document):
	"""Child table for Assessment of Environmental Effects (Schedule 4 RMA)."""

	def before_save(self):
		"""Auto-set is_required flag based on section type."""
		required_sections = ["Activity Description", "Existing Environment", "EffectsSummary"]
		self.is_required = 1 if self.section_type in required_sections else 0
