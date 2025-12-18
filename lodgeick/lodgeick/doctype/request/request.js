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
			// Add universal action bar with all standard actions (immediate)
			add_universal_action_bar(frm);

			// Add application-specific quick actions (immediate)
			add_application_quick_actions(frm);

			// Enhance form sections with visual styling (immediate)
			enhance_form_sections(frm);

			// Defer dashboard-dependent components to allow dashboard initialization
			setTimeout(() => {
				add_status_visualization(frm);
				add_summary_dashboard(frm);
			}, 100);
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
	// Check if dashboard is ready
	if (!frm.dashboard || !frm.dashboard.wrapper) {
		console.warn('Dashboard not ready for summary dashboard');
		return;
	}

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
	// Check if dashboard is ready
	if (!frm.dashboard || !frm.dashboard.wrapper) {
		console.warn('Dashboard not ready for rendering');
		return;
	}

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

/**
 * List View Settings
 * Enhanced list view with color-coded status indicators and custom formatters
 */
frappe.listview_settings['Request'] = {
	add_fields: ['workflow_state', 'priority', 'is_overdue', 'target_completion_date', 'assigned_to'],

	// Color-coded status indicators
	get_indicator: function(doc) {
		const status = doc.workflow_state || 'Draft';
		const indicatorMap = {
			// Draft & Submission states
			'Draft': ['orange', 'Draft'],
			'Submitted': ['blue', 'Submitted'],

			// Processing states
			'Acknowledged': ['cyan', 'Acknowledged'],
			'Processing': ['orange', 'Processing'],

			// RFI states
			'RFI Issued': ['purple', 'RFI Issued'],
			'RFI Received': ['purple', 'RFI Received'],

			// Decision states
			'Pending Decision': ['yellow', 'Pending Decision'],
			'Approved': ['green', 'Approved'],
			'Approved with Conditions': ['green', 'Approved (Conditions)'],
			'Declined': ['red', 'Declined'],

			// Terminal states
			'Withdrawn': ['gray', 'Withdrawn'],
			'Cancelled': ['gray', 'Cancelled'],
			'Completed': ['darkgreen', 'Completed'],

			// Building Consent specific
			'Awaiting Inspection': ['blue', 'Awaiting Inspection'],
			'Inspections Complete': ['green', 'Inspections Complete'],
			'CCC Issued': ['darkgreen', 'CCC Issued'],

			// Appeal state
			'Under Appeal': ['orange', 'Under Appeal']
		};

		return indicatorMap[status] || ['gray', status];
	},

	// Custom formatters for specific columns
	formatters: {
		request_number: function(value, field, doc) {
			// Bold request numbers for easier scanning
			return `<strong>${value}</strong>`;
		},

		target_completion_date: function(value, field, doc) {
			if (!value) return '';

			// Calculate days remaining and add color coding
			const target_date = frappe.datetime.str_to_obj(value);
			const today = frappe.datetime.now_date(true);
			const days_remaining = frappe.datetime.get_day_diff(target_date, today);

			let color = '';
			let icon = '';

			if (days_remaining < 0) {
				color = 'red';
				icon = '<i class="fa fa-exclamation-triangle" style="margin-right: 4px;"></i>';
			} else if (days_remaining <= 5) {
				color = 'orange';
				icon = '<i class="fa fa-clock-o" style="margin-right: 4px;"></i>';
			}

			return `<span style="color: ${color}">${icon}${frappe.datetime.str_to_user(value)}</span>`;
		},

		priority: function(value, field, doc) {
			if (!value) return '';

			// Color-coded priority badges
			const priorityMap = {
				'Urgent': '<span class="badge badge-danger">Urgent</span>',
				'High': '<span class="badge badge-warning">High</span>',
				'Standard': '<span class="badge badge-info">Standard</span>',
				'Low': '<span class="badge badge-secondary">Low</span>'
			};

			return priorityMap[value] || value;
		}
	},

	// Custom filter buttons
	button: {
		show: function(doc) {
			return doc.workflow_state !== 'Completed' && doc.workflow_state !== 'Cancelled';
		},
		get_label: function() {
			return __('View Request');
		},
		get_description: function(doc) {
			return __('Open request details');
		},
		action: function(doc) {
			frappe.set_route('Form', 'Request', doc.name);
		}
	},

	// Quick filter buttons
	onload: function(listview) {
		// Add "Overdue Requests" filter button
		listview.page.add_inner_button(__('Overdue Requests'), function() {
			listview.filter_area.clear();
			listview.filter_area.add([[listview.doctype, 'is_overdue', '=', 1]]);
		});

		// Add "My Assignments" filter button if user is logged in
		if (frappe.session.user !== 'Guest') {
			listview.page.add_inner_button(__('My Assignments'), function() {
				listview.filter_area.clear();
				listview.filter_area.add([[listview.doctype, 'assigned_to', '=', frappe.session.user]]);
			});
		}

		// Add "Active Requests" filter button
		listview.page.add_inner_button(__('Active Requests'), function() {
			listview.filter_area.clear();
			listview.filter_area.add([
				[listview.doctype, 'workflow_state', 'in', ['Processing', 'Acknowledged', 'Pending Decision']]
			]);
		});
	}
};


// ========================================
// NEW: Status Visualization Functions
// ========================================

/**
 * Add status visualization to the form
 */
function add_status_visualization(frm) {
	// Add status pill to page title area
	add_status_pill_to_header(frm);

	// Render status card in the HTML field (NEW!)
	render_status_card(frm);

	// Render requester card (Sprint 3)
	render_requester_card(frm);

	// Render timeline visual (Sprint 3)
	render_timeline_visual(frm);

	// Add workflow progression indicator if workflow is active
	if (frm.doc.workflow_state) {
		add_workflow_progression_indicator(frm);
	}

	// Add SLA countdown if target date exists
	if (frm.doc.target_completion_date) {
		add_sla_countdown_indicator(frm);
	}
}

/**
 * Add status pill to the form header
 */
function add_status_pill_to_header(frm) {
	// Check if page wrapper is ready
	if (!frm.page || !frm.page.wrapper) {
		console.warn('Page wrapper not ready for status pill');
		return;
	}

	// Remove existing status pill
	frm.page.wrapper.find('.form-status-pill').remove();

	if (!frm.doc.workflow_state) return;

	// Import renderStatusPill from status_pill.js
	// Note: These are loaded globally via hooks.py
	if (typeof lodgeick === 'undefined' || typeof lodgeick.status === 'undefined' || typeof lodgeick.status.renderStatusPill === 'undefined') {
		console.error('status_pill.js not loaded');
		return;
	}

	const status_pill_html = lodgeick.status.renderStatusPill(frm.doc.workflow_state);

	// Check if title area is ready
	if (!frm.page.title_area) {
		console.warn('Title area not ready for status pill');
		return;
	}

	// Add to title area
	frm.page.set_secondary_action(() => {}, {
		icon: '',
		size: 'sm'
	});

	$(status_pill_html)
		.addClass('form-status-pill')
		.css({
			'margin-left': '12px',
			'display': 'inline-block',
			'vertical-align': 'middle'
		})
		.insertAfter(frm.page.title_area.find('.title-text'));
}

/**
 * Add workflow progression indicator
 */
function add_workflow_progression_indicator(frm) {
	// Check if dashboard is ready
	if (!frm.dashboard || !frm.dashboard.wrapper) {
		console.warn('Dashboard not ready for workflow progression indicator');
		return;
	}

	// Find or create workflow section in dashboard
	const dashboard = frm.dashboard.wrapper;

	// Remove existing workflow progression
	dashboard.find('.workflow-progression-section').remove();

	if (typeof lodgeick === 'undefined' || typeof lodgeick.workflow === 'undefined' || typeof lodgeick.workflow.renderWorkflowProgression === 'undefined') {
		console.error('workflow_progression.js not loaded');
		return;
	}

	const workflow_html = lodgeick.workflow.renderWorkflowProgression(
		frm.doc.workflow_state,
		frm.doc.request_type,
		frm.doc.request_category
	);

	const section_html = `
		<div class="workflow-progression-section" style="margin: 20px 0;">
			<h6 style="margin-bottom: 12px; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
				Workflow Progress
			</h6>
			${workflow_html}
		</div>
	`;

	dashboard.prepend(section_html);
}

/**
 * Add SLA countdown indicator
 */
function add_sla_countdown_indicator(frm) {
	if (!frm.doc.target_completion_date) return;

	// Check if dashboard is ready
	if (!frm.dashboard || !frm.dashboard.wrapper) {
		console.warn('Dashboard not ready for SLA countdown indicator');
		return;
	}

	// Calculate days remaining
	const target_date = frappe.datetime.str_to_obj(frm.doc.target_completion_date);
	const today = frappe.datetime.now_date(true);
	const days_remaining = frappe.datetime.get_day_diff(target_date, today);

	// Determine SLA status
	let sla_class = 'sla-on-track';
	let sla_icon = 'check-circle';
	let sla_text = `${days_remaining} days remaining`;
	let sla_color = 'green';

	if (days_remaining < 0) {
		sla_class = 'sla-overdue';
		sla_icon = 'alert-triangle';
		sla_text = `${Math.abs(days_remaining)} days overdue`;
		sla_color = 'red';
	} else if (days_remaining <= 5) {
		sla_class = 'sla-warning';
		sla_icon = 'clock';
		sla_text = `${days_remaining} days remaining (urgent)`;
		sla_color = 'orange';
	}

	// Add to dashboard
	const dashboard = frm.dashboard.wrapper;
	dashboard.find('.sla-countdown-section').remove();

	const sla_html = `
		<div class="sla-countdown-section" style="margin: 20px 0;">
			<div class="sla-indicator ${sla_class}">
				<i class="fa fa-${sla_icon}" style="font-size: 18px;"></i>
				<div style="flex: 1;">
					<strong style="display: block;">${sla_text}</strong>
					<small style="opacity: 0.8;">Target: ${frappe.datetime.str_to_user(frm.doc.target_completion_date)}</small>
				</div>
			</div>
		</div>
	`;

	dashboard.prepend(sla_html);

	// Also add prominent indicator if overdue
	if (days_remaining < 0) {
		frm.dashboard.add_comment(
			__('<strong>This request is overdue!</strong> The target completion date has passed. Please prioritize this request or update the timeline.'),
			'red',
			true
		);
	} else if (days_remaining <= 3) {
		frm.dashboard.add_comment(
			__('<strong>Urgent:</strong> This request is due in {0} days.').format(days_remaining),
			'orange',
			true
		);
	}
}

/**
 * Render status card in the HTML field
 */
function render_status_card(frm) {
	const field = frm.get_field('status_card_html');
	if (!field) return;

	// Check if required functions are loaded
	if (typeof lodgeick === 'undefined' || typeof lodgeick.status === 'undefined' || typeof lodgeick.workflow === 'undefined') {
		console.error('Status components not loaded');
		field.$wrapper.html('<p class="text-muted">Loading status components...</p>');
		return;
	}

	// Build status pill
	const status_pill = lodgeick.status.renderStatusPill(frm.doc.workflow_state || 'Draft');

	// Build workflow progression
	const workflow_progression = lodgeick.workflow.renderWorkflowProgression(
		frm.doc.workflow_state || 'Draft',
		frm.doc.request_type,
		frm.doc.request_category
	);

	// Build SLA indicator
	let sla_section = '';
	if (frm.doc.target_completion_date) {
		const target_date = frappe.datetime.str_to_obj(frm.doc.target_completion_date);
		const today = frappe.datetime.now_date(true);
		const days_remaining = frappe.datetime.get_day_diff(target_date, today);

		let sla_class = 'sla-on-track';
		let sla_icon = 'check-circle';
		let sla_text = `${days_remaining} days remaining`;

		if (days_remaining < 0) {
			sla_class = 'sla-overdue';
			sla_icon = 'alert-triangle';
			sla_text = `${Math.abs(days_remaining)} days overdue`;
		} else if (days_remaining <= 5) {
			sla_class = 'sla-warning';
			sla_icon = 'clock';
			sla_text = `${days_remaining} days remaining (urgent)`;
		}

		sla_section = `
			<div class="sla-section" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
				<div class="sla-indicator ${sla_class}">
					<i class="fa fa-${sla_icon}" style="font-size: 18px;"></i>
					<div style="flex: 1; margin-left: 10px;">
						<strong style="display: block;">${sla_text}</strong>
						<small style="opacity: 0.8;">Target: ${frappe.datetime.str_to_user(frm.doc.target_completion_date)}</small>
					</div>
				</div>
			</div>
		`;
	}

	// Combine into status card
	const html = `
		<div class="request-status-card">
			<div class="status-header">
				<h3>Current Status</h3>
				${status_pill}
			</div>
			<div class="workflow-progression">
				${workflow_progression}
			</div>
			${sla_section}
		</div>
	`;

	field.$wrapper.html(html);
}

/**
 * Render requester card in the HTML field
 */
function render_requester_card(frm) {
	const field = frm.get_field('requester_card_html');
	if (!field) return;

	// Get requester initials for avatar
	const get_initials = (name) => {
		if (!name) return '?';
		return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
	};

	const requester_initials = get_initials(frm.doc.requester_name);
	const has_agent = frm.doc.agent && frm.doc.agent_name;

	// Build requester card HTML
	const html = `
		<div class="requester-card">
			<div class="requester-primary">
				<div class="avatar" title="${frm.doc.requester_name || 'No requester'}">${requester_initials}</div>
				<div class="details">
					<h4>${frm.doc.requester_name || 'No Requester'}</h4>
					<p class="text-muted">
						${frm.doc.requester_email ? `<i class="fa fa-envelope"></i> ${frm.doc.requester_email}` : 'No email'}
						${frm.doc.requester_phone ? `<br><i class="fa fa-phone"></i> ${frm.doc.requester_phone}` : ''}
					</p>
					${frm.doc.organization ? `<p class="text-muted"><i class="fa fa-building"></i> ${frm.doc.organization}</p>` : ''}
				</div>
				${frm.doc.requester ? `
					<button class="btn btn-sm btn-default" onclick="frappe.set_route('Form', 'User', '${frm.doc.requester}')">
						View Profile
					</button>
				` : ''}
			</div>
			${has_agent ? `
				<div class="agent-section">
					<h5><i class="fa fa-user-tie"></i> Agent / Representative</h5>
					<p><strong>${frm.doc.agent_name}</strong></p>
					<p class="text-muted">
						${frm.doc.agent_email ? `<i class="fa fa-envelope"></i> ${frm.doc.agent_email}` : ''}
						${frm.doc.agent_phone ? `<br><i class="fa fa-phone"></i> ${frm.doc.agent_phone}` : ''}
					</p>
					<button class="btn btn-xs btn-default" onclick="frappe.set_route('Form', 'User', '${frm.doc.agent}')">
						View Agent Profile
					</button>
				</div>
			` : ''}
		</div>
	`;

	field.$wrapper.html(html);
}

/**
 * Render timeline visual in the HTML field
 */
function render_timeline_visual(frm) {
	const field = frm.get_field('timeline_visual_html');
	if (!field) return;

	// Check if required function is loaded
	if (typeof lodgeick === 'undefined' || typeof lodgeick.timeline === 'undefined' || typeof lodgeick.timeline.renderTimelineVisual === 'undefined') {
		console.error('timeline_visual.js not loaded');
		field.$wrapper.html('<p class="text-muted">Loading timeline component...</p>');
		return;
	}

	// Render timeline
	const html = lodgeick.timeline.renderTimelineVisual(frm);
	field.$wrapper.html(html);
}
