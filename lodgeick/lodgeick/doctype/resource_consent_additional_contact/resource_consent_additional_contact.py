# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResourceConsentAdditionalContact(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email: DF.Data | None
		first_name: DF.Data
		last_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		phone: DF.Data | None
	# end: auto-generated types

	pass
