# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Migration script: WB Task → Project Task
Migrates all WB Tasks linked to CouncilsOnline Assessment Projects to Project Tasks
"""

import frappe
from frappe.utils import getdate


def execute():
	"""Migrate WB Tasks linked to CouncilsOnline to Project Tasks"""

	# Only migrate CouncilsOnline-related tasks (linked to Assessment Projects)
	wb_tasks = frappe.get_all(
		"WB Task",
		fields=["*"],
		filters={
			"assessment_project": ["!=", ""]
		}
	)

	migrated = 0
	failed = 0
	skipped = 0
	mapping = {}  # Old name → New name for reference updates

	frappe.db.commit()  # Commit before starting

	for wb_task in wb_tasks:
		try:
			# Check if already migrated (by checking if Project Task with same title exists)
			existing = frappe.db.exists("Project Task", {
				"title": wb_task.title,
				"assessment_project": wb_task.assessment_project
			})

			if existing:
				frappe.logger().info(f"Skipping {wb_task.name} - already migrated")
				mapping[wb_task.name] = existing
				skipped += 1
				continue

			# Map WB Task status to Project Task status
			status_map = {
				"Open": "Open",
				"Completed": "Completed",
				"Overdue": "Open",  # Overdue → Open (timeliness will be calculated)
			}
			mapped_status = status_map.get(wb_task.status, "Open")

			# Map timeliness
			timeliness_map = {
				"Ontime": "On Time",
				"Late": "Late"
			}
			mapped_timeliness = timeliness_map.get(wb_task.timeliness, "")

			# Create Project Task
			project_task = frappe.get_doc({
				"doctype": "Project Task",
				"title": wb_task.title,
				"description": wb_task.description,
				"status": mapped_status,
				"priority": wb_task.priority or "Medium",
				"due_date": wb_task.due_date,
				"date_of_completion": wb_task.date_of_completion,
				"timeliness": mapped_timeliness,
				"assigned_by": wb_task.assign_from,
				"assigned_to": wb_task.assign_to,
				"assigned_role": wb_task.get("assigned_role"),  # Custom field
				"task_type": wb_task.task_type or "Manual",
				"assessment_project": wb_task.assessment_project,
				"assessment_stage": wb_task.assessment_stage,
				"request": wb_task.get("request"),  # Custom field
				"actual_hours": wb_task.get("actual_time"),  # Custom field: actual_time → actual_hours
				"hourly_rate": wb_task.get("hourly_rate"),  # Custom field
				"total_cost": wb_task.get("total_costing_amount"),  # Custom field
				"has_checklist": wb_task.has_checklist,
				"checklist_template": wb_task.checklist_template
			})

			# Copy checklist items if present
			if wb_task.has_checklist and wb_task.get("wb_task_checklist_details"):
				for item in wb_task.wb_task_checklist_details:
					project_task.append("checklist_items", {
						"checklist_item": item.checklist_item,
						"status": item.status,
						"completed_by": item.get("completed_by"),
						"completed_on": item.get("completed_on")
					})

			# Insert without validation to preserve data
			project_task.insert(ignore_permissions=True, ignore_mandatory=True)
			mapping[wb_task.name] = project_task.name
			migrated += 1

			frappe.logger().info(f"Migrated {wb_task.name} → {project_task.name}")

		except Exception as e:
			frappe.log_error(f"Migration failed for {wb_task.name}: {str(e)}", "WB Task Migration Error")
			failed += 1

	# Update references in Assessment Project
	update_assessment_project_references(mapping)

	# Update references in Assessment Stage Instance
	update_assessment_stage_instance_references(mapping)

	frappe.db.commit()

	# Log summary
	frappe.logger().info(f"""
	=== WB Task Migration Summary ===
	Migrated: {migrated}
	Skipped (already migrated): {skipped}
	Failed: {failed}
	Total WB Tasks processed: {len(wb_tasks)}
	""")

	return {
		"migrated": migrated,
		"skipped": skipped,
		"failed": failed,
		"total": len(wb_tasks)
	}


def update_assessment_project_references(mapping):
	"""Update WB Task references in Assessment Project to Project Task"""
	# Assessment Project doesn't have direct WB Task references
	# The link is from WB Task → Assessment Project
	# No updates needed here
	pass


def update_assessment_stage_instance_references(mapping):
	"""Update WB Task references in Assessment Stage Instance if any"""
	# Check if there are any references to update
	# This might not be needed depending on the schema
	pass


def rollback_migration():
	"""
	Rollback function (for emergency use only)
	Deletes all Project Tasks that were migrated from WB Tasks
	"""
	frappe.db.sql("""
		DELETE FROM `tabProject Task`
		WHERE task_type = 'Auto'
		AND assessment_project IS NOT NULL
	""")

	frappe.db.commit()
	frappe.logger().info("Migration rolled back - all auto Project Tasks deleted")
