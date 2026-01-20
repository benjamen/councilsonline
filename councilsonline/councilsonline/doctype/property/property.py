# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Property(Document):
    def before_save(self):
        """Calculate hectares from square meters"""
        if self.site_area:
            self.site_area_hectares = self.site_area / 10000
