# Copyright (c) 2025, Optified and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, date_diff


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_exclusion_types(doctype, txt, searchfield, start, page_len, filters):
	"""
	Filter exclusion types based on council and request type configuration.
	Only show exclusion types that are enabled for the current council/request type.
	"""
	if not filters:
		return []

	# Get the parent document (Resource Consent Application or Assessment Project)
	parent_doctype = filters.get("parent_doctype")
	parent_name = filters.get("parent_name")

	if not parent_doctype or not parent_name:
		# No filtering - return all exclusion types
		return frappe.db.sql("""
			SELECT name, exclusion_type_name, exclusion_code
			FROM `tabExclusion Type`
			WHERE name LIKE %(txt)s
			ORDER BY is_standard DESC, exclusion_type_name
			LIMIT %(start)s, %(page_len)s
		""", {
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len
		})

	# Get council and request type from parent document
	parent_doc = frappe.get_doc(parent_doctype, parent_name)

	# Determine council and request type
	if hasattr(parent_doc, "council"):
		council = parent_doc.council
	else:
		# If parent doesn't have council, try to get from request
		request_name = getattr(parent_doc, "request", None)
		if request_name:
			request_doc = frappe.get_doc("Request", request_name)
			council = request_doc.council
		else:
			council = None

	if hasattr(parent_doc, "request_type"):
		request_type = parent_doc.request_type
	elif hasattr(parent_doc, "request"):
		request_doc = frappe.get_doc("Request", parent_doc.request)
		request_type = request_doc.request_type
	else:
		request_type = None

	if not council:
		# No council found - return all types
		return frappe.db.sql("""
			SELECT name, exclusion_type_name, exclusion_code
			FROM `tabExclusion Type`
			WHERE name LIKE %(txt)s
			ORDER BY is_standard DESC, exclusion_type_name
			LIMIT %(start)s, %(page_len)s
		""", {
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len
		})

	# Get enabled exclusion types for this council + request type
	query = """
		SELECT DISTINCT et.name, et.exclusion_type_name, et.exclusion_code
		FROM `tabExclusion Type` et
		INNER JOIN `tabCouncil Exclusion Type` cet
			ON cet.exclusion_type = et.name
		WHERE cet.parent = %(council)s
			AND cet.is_enabled = 1
			AND (cet.request_type = %(request_type)s OR cet.request_type IS NULL OR cet.request_type = '')
			AND et.name LIKE %(txt)s
		ORDER BY et.is_standard DESC, et.exclusion_type_name
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, {
		"council": council,
		"request_type": request_type or "",
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})


class ClockExclusionPeriod(Document):
	"""
	Child table for tracking statutory clock suspension periods.

	Automatically calculates working days excluded when ended_date is set.
	Supports linking to reference documents like RFI, custom documents.
	"""

	def validate(self):
		"""Calculate working days when period ends"""
		if self.ended_date and self.started_date:
			self.calculate_working_days_excluded()

	def calculate_working_days_excluded(self):
		"""Calculate working days between start and end dates"""
		from councilsonline.councilsonline.doctype.request.request import calculate_working_days_between

		try:
			start_dt = get_datetime(self.started_date)
			end_dt = get_datetime(self.ended_date)

			if end_dt < start_dt:
				frappe.throw("End date cannot be before start date")

			# Calculate working days (excludes weekends and NZ holidays)
			self.working_days_excluded = calculate_working_days_between(
				start_dt, end_dt
			)
		except Exception as e:
			frappe.log_error(f"Error calculating working days: {str(e)}")
			# Fallback to calendar days / 7 * 5 (rough estimate)
			calendar_days = date_diff(self.ended_date, self.started_date)
			self.working_days_excluded = int(calendar_days / 7 * 5)
