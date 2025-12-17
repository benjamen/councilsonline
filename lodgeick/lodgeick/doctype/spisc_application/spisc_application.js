// Copyright (c) 2025, Optified and contributors
// For license information, please see license.txt

/**
 * SPISC Application Form Script
 * Provides action bar with grouped buttons, summary dashboard, and visual enhancements
 */

frappe.ui.form.on('SPISC Application', {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.request) {
			add_action_buttons(frm);
			add_summary_dashboard(frm);
			add_assessment_quick_actions(frm);
			enhance_sections(frm);
		}
	}
});

// ==================== ACTION BUTTON GROUPS ====================

function add_action_buttons(frm) {
	// === ACTIONS GROUP ===
	frm.add_custom_button(__('View Request'), function() {
		frappe.set_route('Form', 'Request', frm.doc.request);
	}, __('Actions'));

	frm.add_custom_button(__('View Assessment Project'), function() {
		open_assessment_project(frm);
	}, __('Actions'));

	// === TASKS GROUP ===
	frm.add_custom_button(__('View Tasks'), function() {
		show_linked_tasks(frm);
	}, __('Tasks'));

	frm.add_custom_button(__('Create Task'), function() {
		create_task_for_application(frm);
	}, __('Tasks'));

	// === MEETINGS GROUP ===
	frm.add_custom_button(__('View Meetings'), function() {
		show_linked_meetings(frm);
	}, __('Meetings'));

	frm.add_custom_button(__('Schedule Meeting'), function() {
		schedule_meeting_for_application(frm);
	}, __('Meetings'));

	// === COMMUNICATIONS GROUP ===
	frm.add_custom_button(__('View Communications'), function() {
		show_linked_communications(frm);
	}, __('Communications'));

	frm.add_custom_button(__('Send Notification'), function() {
		send_notification_to_applicant(frm);
	}, __('Communications'));

	frm.add_custom_button(__('Add Internal Note'), function() {
		add_internal_note(frm);
	}, __('Communications'));
}

// ==================== SUMMARY DASHBOARD ====================

function add_summary_dashboard(frm) {
	// Remove existing dashboard if present
	frm.layout.wrapper.find('.spisc-summary-dashboard').remove();

	// Fetch counts via API
	frappe.call({
		method: 'lodgeick.api.get_spisc_summary_data',
		args: { request_id: frm.doc.request },
		callback: function(r) {
			if (r.message) {
				render_summary_dashboard(frm, r.message);
			}
		}
	});
}

function render_summary_dashboard(frm, data) {
	const summary_html = `
		<div class="spisc-summary-dashboard" style="
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			color: white;
			padding: 20px;
			border-radius: 8px;
			margin-bottom: 20px;
			box-shadow: 0 4px 6px rgba(0,0,0,0.1);
		">
			<div style="font-size: 18px; font-weight: 600; margin-bottom: 15px;">
				📊 Application Overview
			</div>
			<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
				<div class="dashboard-metric">
					<div style="font-size: 24px; font-weight: bold;">${data.tasks_count || 0}</div>
					<div style="font-size: 12px; opacity: 0.9;">Open Tasks</div>
				</div>
				<div class="dashboard-metric">
					<div style="font-size: 24px; font-weight: bold;">${data.meetings_count || 0}</div>
					<div style="font-size: 12px; opacity: 0.9;">Meetings</div>
				</div>
				<div class="dashboard-metric">
					<div style="font-size: 24px; font-weight: bold;">${data.communications_count || 0}</div>
					<div style="font-size: 12px; opacity: 0.9;">Communications</div>
				</div>
				<div class="dashboard-metric">
					<div style="font-size: 24px; font-weight: bold;">${data.assessment_status || 'N/A'}</div>
					<div style="font-size: 12px; opacity: 0.9;">Assessment</div>
				</div>
				<div class="dashboard-metric">
					<div style="font-size: 24px; font-weight: bold;">${data.eligibility_status || 'Pending'}</div>
					<div style="font-size: 12px; opacity: 0.9;">Eligibility</div>
				</div>
			</div>
		</div>
	`;

	$(summary_html).prependTo(frm.layout.wrapper.find('.form-layout'));
}

// ==================== ASSESSMENT QUICK ACTIONS ====================

function add_assessment_quick_actions(frm) {
	// Add quick eligibility assessment button if not already assessed
	if (frm.doc.eligibility_status === 'Pending') {
		frm.add_custom_button(__('Quick Assess Eligibility'), function() {
			quick_assess_eligibility(frm);
		}, __('Assessment'));
	}

	// Link to detailed assessment
	frm.add_custom_button(__('Detailed Assessment'), function() {
		open_assessment_project(frm);
	}, __('Assessment'));
}

function quick_assess_eligibility(frm) {
	frappe.call({
		method: 'lodgeick.lodgeick.doctype.spisc_application.spisc_application.assess_eligibility',
		args: { name: frm.doc.name },
		callback: function(r) {
			if (!r.exc) {
				frm.reload_doc();
				frappe.show_alert({
					message: __('Eligibility Assessment Complete'),
					indicator: 'green'
				});
			}
		}
	});
}

// ==================== LINKED DOCUMENTS DISPLAY ====================

function show_linked_tasks(frm) {
	frappe.route_options = { "request": frm.doc.request };
	frappe.set_route("List", "Project Task");
}

function show_linked_meetings(frm) {
	frappe.route_options = { "request": frm.doc.request };
	frappe.set_route("List", "Pre-Application Meeting");
}

function show_linked_communications(frm) {
	frappe.route_options = { "request": frm.doc.request };
	frappe.set_route("List", "Communication Log");
}

function open_assessment_project(frm) {
	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			doctype: 'Assessment Project',
			filters: { request: frm.doc.request },
			fieldname: 'name'
		},
		callback: function(r) {
			if (r.message && r.message.name) {
				frappe.set_route('Form', 'Assessment Project', r.message.name);
			} else {
				frappe.msgprint({
					title: __('No Assessment Project'),
					message: __('No Assessment Project found for this application. Would you like to create one?'),
					primary_action: {
						label: __('Create Assessment'),
						action: () => create_assessment_project(frm)
					}
				});
			}
		}
	});
}

// ==================== CREATE NEW LINKED DOCUMENTS ====================

function create_task_for_application(frm) {
	frappe.new_doc('Project Task', {
		request: frm.doc.request,
		subject: `SPISC Application - ${frm.doc.applicant_name || 'Task'}`,
		description: `Related to SPISC Application ${frm.doc.name}`
	});
}

function schedule_meeting_for_application(frm) {
	frappe.new_doc('Pre-Application Meeting', {
		request: frm.doc.request,
		meeting_type: 'Assessment Meeting',
		requester_name: frm.doc.applicant_name,
		requester_email: frm.doc.applicant_email,
		requester_phone: frm.doc.applicant_phone
	});
}

function send_notification_to_applicant(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Send Notification to Applicant'),
		fields: [
			{
				label: __('Subject'),
				fieldname: 'subject',
				fieldtype: 'Data',
				reqd: 1
			},
			{
				label: __('Message'),
				fieldname: 'message',
				fieldtype: 'Text Editor',
				reqd: 1
			}
		],
		primary_action_label: __('Send'),
		primary_action: function(values) {
			frappe.call({
				method: 'lodgeick.api.send_notification_to_applicant',
				args: {
					request: frm.doc.request,
					subject: values.subject,
					message: values.message
				},
				callback: function(r) {
					if (!r.exc) {
						frappe.show_alert({
							message: __('Notification sent successfully'),
							indicator: 'green'
						});
						d.hide();
					}
				}
			});
		}
	});
	d.show();
}

function add_internal_note(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Add Internal Note'),
		fields: [
			{
				label: __('Subject'),
				fieldname: 'subject',
				fieldtype: 'Data',
				reqd: 1
			},
			{
				label: __('Note'),
				fieldname: 'content',
				fieldtype: 'Text Editor',
				reqd: 1
			}
		],
		primary_action_label: __('Save'),
		primary_action: function(values) {
			frappe.call({
				method: 'lodgeick.api.add_internal_note',
				args: {
					request: frm.doc.request,
					subject: values.subject,
					content: values.content
				},
				callback: function(r) {
					if (!r.exc) {
						frappe.show_alert({
							message: __('Internal note saved'),
							indicator: 'green'
						});
						d.hide();
					}
				}
			});
		}
	});
	d.show();
}

function create_assessment_project(frm) {
	frappe.call({
		method: 'lodgeick.api.create_assessment_project_for_request',
		args: {
			request: frm.doc.request,
			request_type: 'Social Pension for Indigent Senior Citizens (SPISC)'
		},
		callback: function(r) {
			if (r.message) {
				frappe.set_route('Form', 'Assessment Project', r.message.name);
			}
		}
	});
}

// ==================== VISUAL SECTION ENHANCEMENTS ====================

function enhance_sections(frm) {
	// Highlight applicant information section
	const applicant_section = frm.fields_dict['applicant_details_section'];
	if (applicant_section && applicant_section.wrapper) {
		$(applicant_section.wrapper).css({
			'background-color': '#f0f9ff',
			'border-radius': '6px',
			'padding': '15px',
			'border-left': '4px solid #3b82f6'
		});
	}

	// Highlight assessment section for council staff
	const assessment_section = frm.fields_dict['assessment_section'];
	if (assessment_section && assessment_section.wrapper) {
		$(assessment_section.wrapper).css({
			'background-color': '#fef3c7',
			'border-radius': '6px',
			'padding': '15px',
			'border-left': '4px solid #f59e0b'
		});

		// Add section label
		const section_head = $(assessment_section.wrapper).find('.section-head');
		if (section_head.find('.section-label').length === 0) {
			section_head.append('<span class="section-label" style="color: #92400e; font-weight: 600; margin-left: 10px;">🏛️ Council Staff Only</span>');
		}
	}
}
