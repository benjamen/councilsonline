# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TaskTemplateChecklistItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		checklist_item: DF.Data | None
		is_mandatory: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
