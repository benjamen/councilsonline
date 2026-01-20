# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CouncilLandingPage(Document):
    """Council Landing Page DocType controller"""

    def validate(self):
        """Validate Council Landing Page document"""
        # Ensure council exists and is active
        if self.council:
            council = frappe.get_doc("Council", self.council)
            if not council.is_active:
                frappe.throw(frappe._(
                    "Cannot create landing page for inactive council: {0}"
                ).format(self.council))

        # Set default hero title if empty
        if not self.hero_title and self.council:
            council = frappe.get_doc("Council", self.council)
            self.hero_title = f"Welcome to {council.council_name}"

        # Set default hero subtitle if empty
        if not self.hero_subtitle:
            self.hero_subtitle = (
                "Submit planning applications, building consents, and resource consent requests online"
            )

# --- Website Page Controller ---
def get_context(context):
    """
    Populate the context for the council landing page template.
    Handles Vue frontend base URL and council lookup safely.
    """
    # Extract council code from the URL after /frontend/
    path = frappe.request.path  # e.g., "/frontend/taytay-ph"
    path_parts = path.strip("/").split("/")
    council_code = path_parts[1] if len(path_parts) > 1 else None

    # Fetch council safely
    if council_code and frappe.db.exists("Council", council_code):
        council = frappe.get_doc("Council", council_code)
    else:
        council = None
        frappe.local.user_data = {"council_missing": True}

    # Set user/session data safely
    if getattr(frappe.local.session, "set_user_data", None):
        frappe.local.session.set_user_data({"council": council_code})
    else:
        frappe.local.user_data = {"council": council_code}

    # Populate template context
    context.council = council
    context.hero_title = f"Welcome to {council.council_name}" if council else "Welcome"
    context.hero_subtitle = (
        "Submit planning applications, building consents, and resource consent requests online"
    )

    return context
