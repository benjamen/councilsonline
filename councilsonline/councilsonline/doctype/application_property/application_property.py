# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ApplicationProperty(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		area_hectares: DF.Float | None
		legal_description: DF.Text | None
		property: DF.Link | None
		property_address: DF.Data | None
		property_valuation_number: DF.Data | None
	# end: auto-generated types

	pass
