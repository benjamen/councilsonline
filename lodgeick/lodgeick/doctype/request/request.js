// Copyright (c) 2025, Optified and contributors
// For license information, please see license.txt

/**
 * Request Form - Central Hub for All Request Types
 *
 * This is the main interface for council staff to manage requests.
 * Provides universal action bar with Tasks, Meetings, Communications, and Assessment Project access.
 */

frappe.ui.form.on("Request", {
	refresh: function(frm) {
		if (!frm.is_new()) {
			// Add universal action bar with all standard actions
			add_universal_action_bar(frm);

			// Add summary dashboard showing key metrics
			add_summary_dashboard(frm);

			// Add application-specific quick actions
			add_application_quick_actions(frm);

			// Enhance form sections with visual styling
			enhance_form_sections(frm);
		}
	},

	onload: function(frm) {
		// Set up any field filters or queries
		setup_field_queries(frm);
	}
});


/**
 * Add universal action bar with all standard request actions
 */
function add_universal_action_bar(frm) {
	// Clear existing custom buttons to avoid duplicates
	frm.clear_custom_buttons();

	// === ACTIONS GROUP ===
	frm.add_custom_button(__('View Application'), function() {
		view_application(frm);
	}, __('Actions'));

	frm.add_custom_button(__('View Assessment Project'), function() {
		open_assessment_project(frm);
	}, __('Actions'));

	// === TASKS GROUP ===
	frm.add_custom_button(__('View Tasks'), function() {
		view_linked_documents(frm, 'Project Task');
	}, __('Tasks'));

	frm.add_custom_button(__('Create Task'), function() {
		create_task(frm);
	}, __('Tasks'));

	// === MEETINGS GROUP ===
	frm.add_custom_button(__('View Meetings'), function() {
		view_linked_documents(frm, 'Council Meeting');
	}, __('Meetings'));

	frm.add_custom_button(__('Schedule Meeting'), function() {
		schedule_meeting(frm);
	}, __('Meetings'));

	// === COMMUNICATIONS GROUP ===
	frm.add_custom_button(__('View Communications'), function() {
		view_linked_documents(frm, 'Communication Log');
	}, __('Communications'));

	frm.add_custom_button(__('Send Notification'), function() {
		send_notification(frm);
	}, __('Communications'));

	frm.add_custom_button(__('Add Internal Note'), function() {
		add_internal_note(frm);
	}, __('Communications'));

	// === DOCUMENTS GROUP ===
	frm.add_custom_button(__('View Documents'), function() {
		view_linked_documents(frm, 'File');
	}, __('Documents'));

	frm.add_custom_button(__('Upload Document'), function() {
		upload_document(frm);
	}, __('Documents'));
}


/**
 * Add summary dashboard with key metrics
 */
function add_summary_dashboard(frm) {
	// Remove existing dashboard if present
	frm.dashboard.wrapper.find('.request-summary-dashboard').remove();

	// Fetch summary data
	frappe.call({
		method: 'lodgeick.api.get_request_summary_data',
		args: {
			request_id: frm.doc.name
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				render_dashboard(frm, r.message);
			}
		}
	});
}


/**
 * Render the summary dashboard
 */
function render_dashboard(frm, data) {
	// Determine dashboard color based on request type
	let dashboard_color = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'; // Default purple

	if (data.request_type === 'Resource Consent') {
		dashboard_color = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'; // Pink/red for RC
	} else if (data.request_type.includes('SPISC')) {
		dashboard_color = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'; // Blue for SPISC
	} else if (data.request_type === 'Building Consent') {
		dashboard_color = 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'; // Green for BC
	}

	// Build metrics HTML
	const metrics = [];

	// Tasks metric
	metrics.push(create_metric_html(
		'Tasks',
		`${data.open_tasks_count}/${data.tasks_count}`,
		'check-square',
		'#3498db'
	));

	// Meetings metric
	metrics.push(create_metric_html(
		'Meetings',
		data.meetings_count,
		'calendar',
		'#9b59b6'
	));

	// Communications metric
	metrics.push(create_metric_html(
		'Communications',
		data.communications_count,
		'message-square',
		'#e74c3c'
	));

	// Assessment Status metric
	metrics.push(create_metric_html(
		'Assessment',
		data.assessment_status,
		'award',
		'#27ae60',
		true // is_status
	));

	// Current Stage metric (if assessment exists)
	if (data.current_stage && data.current_stage !== 'N/A') {
		metrics.push(create_metric_html(
			'Current Stage',
			data.current_stage,
			'layers',
			'#f39c12',
			true // is_status
		));
	}

	// Application-specific metrics
	if (data.eligibility_status) {
		metrics.push(create_metric_html(
			'Eligibility',
			data.eligibility_status,
			'user-check',
			'#16a085',
			true
		));
	}

	if (data.statutory_clock_status) {
		metrics.push(create_metric_html(
			'Clock Status',
			`${data.statutory_clock_status} (${data.days_elapsed}d)`,
			'clock',
			'#d35400',
			true
		));
	}

	const metrics_html = metrics.join('<div style="width: 1px; background: rgba(255,255,255,0.2); margin: 10px 0;"></div>');

	const dashboard_html = `
		<div class="request-summary-dashboard" style="
			background: ${dashboard_color};
			padding: 15px 20px;
			margin: -15px -15px 15px -15px;
			border-radius: 5px;
			color: white;
			box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		">
			<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
				${metrics_html}
			</div>
		</div>
	`;

	frm.dashboard.wrapper.prepend(dashboard_html);
}


/**
 * Create metric HTML
 */
function create_metric_html(label, value, icon, color, is_status = false) {
	const display_value = is_status ? value : `<strong>${value}</strong>`;
	const font_size = is_status ? '14px' : '24px';

	return `
		<div class="dashboard-metric" style="flex: 1; text-align: center; padding: 10px; min-width: 100px;">
			<div style="font-size: 12px; color: rgba(255,255,255,0.9); margin-bottom: 5px;">
				<svg class="icon icon-sm" style="width: 14px; height: 14px; margin-right: 5px; vertical-align: middle;">
					<use href="#icon-${icon}"></use>
				</svg>
				${label}
			</div>
			<div style="font-size: ${font_size}; color: white; font-weight: ${is_status ? 'normal' : 'bold'};">
				${display_value}
			</div>
		</div>
	`;
}


/**
 * Add application-specific quick actions
 */
function add_application_quick_actions(frm) {
	// Add quick action based on request type
	if (frm.doc.request_type === 'Social Pension for Indigent Senior Citizens (SPISC)') {
		// SPISC-specific actions could go here
	} else if (frm.doc.request_type === 'Resource Consent') {
		// RC-specific actions could go here
	}
}


/**
 * Enhance form sections with visual styling
 */
function enhance_form_sections(frm) {
	// Add visual indicators for workflow state
	const workflow_state = frm.doc.workflow_state;
	if (workflow_state) {
		const state_colors = {
			'Draft': '#95a5a6',
			'Submitted': '#3498db',
			'Under Review': '#f39c12',
			'Approved': '#27ae60',
			'Rejected': '#e74c3c',
			'Completed': '#16a085'
		};

		const color = state_colors[workflow_state] || '#95a5a6';
		frm.set_indicator_formatter('workflow_state',
			function(doc) {
				return workflow_state;
			}
		);
	}
}


/**
 * Set up field queries and filters
 */
function setup_field_queries(frm) {
	// Filter assessment project to only show projects linked to this request
	frm.set_query('assessment_project', function() {
		return {
			filters: {
				request: frm.doc.name
			}
		};
	});
}


// ==================== ACTION BUTTON FUNCTIONS ====================

/**
 * View the application form for this request
 */
function view_application(frm) {
	if (frm.doc.application_doctype && frm.doc.application_name) {
		frappe.set_route('Form', frm.doc.application_doctype, frm.doc.application_name);
	} else {
		frappe.msgprint({
			title: __('No Application'),
			message: __('No application has been created for this request yet.'),
			indicator: 'orange'
		});
	}
}


/**
 * Open the Assessment Project
 */
function open_assessment_project(frm) {
	if (frm.doc.assessment_project) {
		frappe.set_route('Form', 'Assessment Project', frm.doc.assessment_project);
	} else {
		// Check if assessment project exists but isn't linked yet
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Assessment Project',
				filters: { request: frm.doc.name },
				fieldname: 'name'
			},
			callback: function(r) {
				if (r.message && r.message.name) {
					frappe.set_route('Form', 'Assessment Project', r.message.name);
				} else {
					frappe.msgprint({
						title: __('No Assessment Project'),
						message: __('No Assessment Project has been created for this request yet.'),
						indicator: 'orange'
					});
				}
			}
		});
	}
}


/**
 * View linked documents
 */
function view_linked_documents(frm, doctype) {
	frappe.route_options = {
		"request": frm.doc.name
	};
	frappe.set_route("List", doctype);
}


/**
 * Create a new task linked to this request
 */
function create_task(frm) {
	frappe.new_doc('Project Task', {
		request: frm.doc.name,
		project: frm.doc.assessment_project || '',
		subject: `Task for ${frm.doc.name}`
	});
}


/**
 * Schedule a council meeting
 */
function schedule_meeting(frm) {
	frappe.new_doc('Council Meeting', {
		request: frm.doc.name,
		meeting_title: `Meeting for ${frm.doc.name} - ${frm.doc.requester_name}`
	});
}


/**
 * Send notification to requester
 */
function send_notification(frm) {
	const d = new frappe.ui.Dialog({
		title: __('Send Notification'),
		fields: [
			{
				label: __('Subject'),
				fieldname: 'subject',
				fieldtype: 'Data',
				reqd: 1,
				default: `Update on Request ${frm.doc.name}`
			},
			{
				label: __('Message'),
				fieldname: 'message',
				fieldtype: 'Text Editor',
				reqd: 1
			},
			{
				label: __('Send Via'),
				fieldname: 'channel',
				fieldtype: 'Select',
				options: ['Email', 'SMS', 'Both'],
				default: 'Email',
				reqd: 1
			}
		],
		primary_action_label: __('Send'),
		primary_action(values) {
			frappe.call({
				method: 'lodgeick.api.send_request_notification',
				args: {
					request_id: frm.doc.name,
					subject: values.subject,
					message: values.message,
					channel: values.channel
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.msgprint({
							title: __('Notification Sent'),
							message: __('Notification has been sent successfully.'),
							indicator: 'green'
						});
						d.hide();
						frm.reload_doc();
					}
				}
			});
		}
	});

	d.show();
}


/**
 * Add internal note
 */
function add_internal_note(frm) {
	const d = new frappe.ui.Dialog({
		title: __('Add Internal Note'),
		fields: [
			{
				label: __('Note'),
				fieldname: 'note',
				fieldtype: 'Text Editor',
				reqd: 1
			},
			{
				label: __('Visibility'),
				fieldname: 'visibility',
				fieldtype: 'Select',
				options: ['Internal Only', 'Share with Team'],
				default: 'Internal Only',
				reqd: 1
			}
		],
		primary_action_label: __('Add Note'),
		primary_action(values) {
			frappe.call({
				method: 'lodgeick.api.add_internal_note',
				args: {
					request_id: frm.doc.name,
					note: values.note,
					visibility: values.visibility
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.msgprint({
							title: __('Note Added'),
							message: __('Internal note has been added successfully.'),
							indicator: 'green'
						});
						d.hide();
						frm.reload_doc();
					}
				}
			});
		}
	});

	d.show();
}


/**
 * Upload document
 */
function upload_document(frm) {
	new frappe.ui.FileUploader({
		doctype: frm.doc.doctype,
		docname: frm.doc.name,
		frm: frm,
		folder: 'Home/Attachments',
		on_success(file_doc) {
			frappe.msgprint({
				title: __('Document Uploaded'),
				message: __('Document {0} has been uploaded successfully.').format(file_doc.file_name),
				indicator: 'green'
			});
			frm.reload_doc();
		}
	});
}
