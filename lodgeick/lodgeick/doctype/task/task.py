# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_my_tasks():
    """Get tasks - migrated to Project Task"""
    # Note: Migrated from WB Task (Workboard app) to native Project Task
    # TODO: Implement get_my_tasks for Project Task doctype
    return []

    # Legacy code (used WB Task from Workboard app - now removed):
    # return frappe.get_all(
    #     "Project Task",
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
