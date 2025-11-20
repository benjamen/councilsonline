# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_my_tasks():
    """Get tasks - WB Task integration disabled"""
    # Note: WB Task doctype from Workboard app is not installed
    # Returning empty list until Workboard integration is configured
    return []

    # Original code commented out - requires Workboard app installation:
    # return frappe.get_all(
    #     "WB Task",
    #     fields=[
    #         "name",
    #         "title",
    #         "description",
    #         "status",
    #         "priority",
    #         "assign_to",
    #         "assign_from",
    #         "due_date",
    #         "date_of_completion",
    #         "timeliness",
    #         "task_type",
    #         "has_checklist",
    #         "creation",
    #         "modified"
    #     ],
    #     filters={
    #         "status": ["!=", "Cancelled"]
    #     },
    #     order_by="creation desc",
    #     limit=100
    # )
