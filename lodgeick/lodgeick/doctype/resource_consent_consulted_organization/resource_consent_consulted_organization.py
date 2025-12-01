# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResourceConsentConsultedOrganization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		city: DF.Data | None
		concern_details: DF.Text | None
		contact_name: DF.Data | None
		email: DF.Data | None
		had_concerns: DF.Check
		is_iwi: DF.Check
		organisation_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		phone: DF.Data | None
		postcode: DF.Data | None
		rd_number: DF.Data | None
		resolution_details: DF.Text | None
		suburb: DF.Data | None
	# end: auto-generated types

	pass
