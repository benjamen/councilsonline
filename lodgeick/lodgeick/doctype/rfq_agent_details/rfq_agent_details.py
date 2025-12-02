# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class RFQAgentDetails(Document):
	def before_save(self):
		"""Update timestamps and status based on actions"""
		# If status changed to "Sent to Agent", record sent date
		if self.status == "Sent to Agent" and not self.sent_date:
			self.sent_date = now_datetime()

		# If status changed to "Quote Received", record received date
		if self.status == "Quote Received" and not self.quote_received_date:
			self.quote_received_date = now_datetime()

		# If status changed to "Quote Accepted", record accepted date
		if self.status == "Quote Accepted" and not self.quote_accepted_date:
			self.quote_accepted_date = now_datetime()

		# If status changed to "Agent Engaged", record engaged date and lock request
		if self.status == "Agent Engaged" and not self.agent_engaged_date:
			self.agent_engaged_date = now_datetime()
			self._lock_request()

	def _lock_request(self):
		"""Lock the associated request from further edits by applicant"""
		if self.request:
			try:
				request_doc = frappe.get_doc("Request", self.request)
				request_doc.agent_engaged = 1
				request_doc.agent_id = self.agent
				request_doc.locked_for_editing = 1
				request_doc.locked_reason = f"Agent engaged on {self.agent_engaged_date}"
				request_doc.save(ignore_permissions=True)
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					title="RFQ - Failed to lock request",
					message=f"Request: {self.request}, Error: {str(e)}"
				)

	def on_submit(self):
		"""Actions when RFQ is submitted"""
		# Update status to "Sent to Agent" if still draft
		if self.status == "Draft":
			self.status = "Sent to Agent"
			self.sent_date = now_datetime()
			self.save()


@frappe.whitelist()
def create_rfq_for_request(request_id, rfq_message=None):
	"""
	Create a new RFQ Agent Details document for a request

	Args:
		request_id: Request document name
		rfq_message: Optional custom RFQ message (uses default if not provided)

	Returns:
		dict: RFQ document details
	"""
	# Check if request exists
	if not frappe.db.exists("Request", request_id):
		frappe.throw(frappe._("Request not found"))

	# Check if RFQ already exists for this request
	existing_rfq = frappe.db.get_value(
		"RFQ Agent Details",
		{"request": request_id, "status": ["!=", "Cancelled"]},
		"name"
	)

	if existing_rfq:
		frappe.throw(frappe._("An active RFQ already exists for this request"))

	# Create new RFQ
	rfq = frappe.get_doc({
		"doctype": "RFQ Agent Details",
		"request": request_id,
		"status": "Draft"
	})

	# Set custom message if provided
	if rfq_message:
		rfq.rfq_message = rfq_message

	rfq.flags.ignore_permissions = True
	rfq.insert()
	frappe.db.commit()

	return {
		"success": True,
		"rfq_id": rfq.name,
		"rfq_message": rfq.rfq_message
	}


@frappe.whitelist()
def send_rfq_to_agent(rfq_id, agent_id):
	"""
	Send RFQ to selected agent

	Args:
		rfq_id: RFQ Agent Details document name
		agent_id: User ID of the agent

	Returns:
		dict: Success status
	"""
	rfq = frappe.get_doc("RFQ Agent Details", rfq_id)

	# Update RFQ with selected agent
	rfq.selected_agent = agent_id
	rfq.agent = agent_id
	rfq.status = "Sent to Agent"
	rfq.sent_date = now_datetime()
	rfq.notification_sent = 1

	# Add notification log
	log_entry = f"{now_datetime()}: RFQ sent to agent {agent_id}\n"
	rfq.notification_log = (rfq.notification_log or "") + log_entry

	rfq.save(ignore_permissions=True)

	# TODO: Send actual email notification to agent
	# This would integrate with your notification system

	frappe.db.commit()

	return {
		"success": True,
		"message": "RFQ sent to agent successfully"
	}


@frappe.whitelist()
def engage_agent(rfq_id):
	"""
	Engage the agent - locks the request from further edits

	Args:
		rfq_id: RFQ Agent Details document name

	Returns:
		dict: Success status
	"""
	rfq = frappe.get_doc("RFQ Agent Details", rfq_id)

	if not rfq.agent:
		frappe.throw(frappe._("No agent selected for this RFQ"))

	# Update status to "Agent Engaged"
	rfq.status = "Agent Engaged"
	rfq.agent_engaged_date = now_datetime()

	rfq.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"message": "Agent engaged successfully. Request is now locked for editing.",
		"agent_id": rfq.agent
	}


@frappe.whitelist()
def get_available_agents(council_code=None):
	"""
	Get list of available agents (users with Agent role)

	Args:
		council_code: Optional council code to filter agents

	Returns:
		list: List of agent users
	"""
	# Get users with Agent role
	agents = frappe.get_all(
		"User",
		filters={
			"enabled": 1,
			"name": ["in", frappe.get_list(
				"Has Role",
				filters={"role": "Agent", "parenttype": "User"},
				pluck="parent"
			)]
		},
		fields=["name", "full_name", "email", "phone"],
		order_by="full_name asc"
	)

	return agents
