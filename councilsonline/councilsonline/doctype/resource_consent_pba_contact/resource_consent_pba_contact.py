# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResourceConsentPBAContact(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		city: DF.Data | None
		contact_name: DF.Data
		email: DF.Data | None
		organisation_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		phone: DF.Data | None
		postcode: DF.Data | None
		rd_number: DF.Data | None
		suburb: DF.Data | None
	# end: auto-generated types

	pass
