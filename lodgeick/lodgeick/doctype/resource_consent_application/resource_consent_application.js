// Copyright (c) 2025, Lodgeick and contributors
// For license information, please see license.txt

frappe.ui.form.on('Resource Consent Application', {
	refresh: function(frm) {
		// Add custom styling and UI enhancements
		add_statutory_clock_indicator(frm);
		add_summary_dashboard(frm);
		enhance_request_info_section(frm);
		style_applicant_fields(frm);
		make_applicant_fields_readonly(frm);
		add_custom_buttons(frm);
	},

	onload: function(frm) {
		// Set up field dependencies
		setup_field_visibility(frm);
	}
});

/**
 * Add statutory clock indicator to the top of the form
 */
function add_statutory_clock_indicator(frm) {
	if (!frm.doc.statutory_clock_started) {
		return;
	}

	const days_elapsed = frm.doc.working_days_elapsed || 0;
	const days_remaining = frm.doc.working_days_remaining || 0;
	const total_days = days_elapsed + days_remaining;
	const percentage = total_days > 0 ? (days_elapsed / total_days) * 100 : 0;

	// Check if clock is currently running
	const is_running = frm.doc.statutory_clock_started && !frm.doc.statutory_clock_stopped;

	// Determine status color
	let status_color = 'green';
	let status_text = 'On Track';
	if (!is_running) {
		status_color = 'gray';
		status_text = 'Stopped';
	} else if (percentage > 80) {
		status_color = 'red';
		status_text = 'Urgent';
	} else if (percentage > 60) {
		status_color = 'orange';
		status_text = 'Monitor';
	}

	// Calculate days since last start/stop for display
	let runtime_info = '';
	if (is_running && frm.doc.statutory_clock_started) {
		const now = new Date();
		const started = new Date(frm.doc.statutory_clock_started);
		const calendar_days = Math.floor((now - started) / (1000 * 60 * 60 * 24));
		runtime_info = `Running for ${calendar_days} calendar day${calendar_days !== 1 ? 's' : ''}`;
	} else if (frm.doc.statutory_clock_stopped) {
		const stopped = new Date(frm.doc.statutory_clock_stopped);
		const started = new Date(frm.doc.statutory_clock_started);
		const calendar_days = Math.floor((stopped - started) / (1000 * 60 * 60 * 24));
		runtime_info = `Stopped after ${calendar_days} calendar day${calendar_days !== 1 ? 's' : ''}`;
	}

	// Format dates for display
	const format_datetime = (dt) => {
		if (!dt) return 'N/A';
		const date = new Date(dt);
		return date.toLocaleString('en-NZ', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	};

	// Create comprehensive clock summary panel
	const clock_html = `
		<div class="statutory-clock-indicator" style="
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			color: white;
			padding: 20px;
			margin: -15px -15px 20px -15px;
			border-radius: 8px 8px 0 0;
			box-shadow: 0 4px 6px rgba(0,0,0,0.1);
		">
			<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
				<div style="flex: 1;">
					<div style="font-size: 11px; text-transform: uppercase; opacity: 0.8; margin-bottom: 5px; letter-spacing: 0.5px;">
						🕐 Statutory Clock Status
					</div>
					<div style="font-size: 28px; font-weight: bold; line-height: 1.2;">
						${days_elapsed} working days
					</div>
					<div style="font-size: 13px; opacity: 0.9; margin-top: 5px;">
						${days_remaining} day${days_remaining !== 1 ? 's' : ''} remaining of ${total_days} total
					</div>
				</div>
				<div style="text-align: right;">
					<div style="
						background: ${status_color === 'green' ? '#10b981' : status_color === 'orange' ? '#f59e0b' : status_color === 'red' ? '#ef4444' : '#6b7280'};
						padding: 10px 18px;
						border-radius: 20px;
						font-size: 13px;
						font-weight: 600;
						display: inline-block;
						box-shadow: 0 2px 4px rgba(0,0,0,0.2);
						margin-bottom: 8px;
					">
						${is_running ? '▶' : '⏸'} ${status_text}
					</div>
					<div style="font-size: 11px; opacity: 0.85;">
						${Math.round(percentage)}% elapsed
					</div>
				</div>
			</div>

			<!-- Progress Bar -->
			<div style="margin-bottom: 15px; background: rgba(255,255,255,0.2); border-radius: 10px; height: 10px; overflow: hidden;">
				<div style="
					width: ${percentage}%;
					height: 100%;
					background: ${status_color === 'red' ? '#ef4444' : status_color === 'orange' ? '#f59e0b' : status_color === 'gray' ? '#6b7280' : '#10b981'};
					transition: width 0.3s ease;
					box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
				"></div>
			</div>

			<!-- Clock Details Grid -->
			<div style="
				display: grid;
				grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
				gap: 12px;
				background: rgba(255,255,255,0.1);
				padding: 12px;
				border-radius: 6px;
			">
				<div>
					<div style="font-size: 10px; text-transform: uppercase; opacity: 0.7; margin-bottom: 4px;">
						Last Started
					</div>
					<div style="font-size: 12px; font-weight: 500;">
						${format_datetime(frm.doc.statutory_clock_started)}
					</div>
				</div>
				<div>
					<div style="font-size: 10px; text-transform: uppercase; opacity: 0.7; margin-bottom: 4px;">
						Last Stopped
					</div>
					<div style="font-size: 12px; font-weight: 500;">
						${format_datetime(frm.doc.statutory_clock_stopped)}
					</div>
				</div>
				<div>
					<div style="font-size: 10px; text-transform: uppercase; opacity: 0.7; margin-bottom: 4px;">
						Current Status
					</div>
					<div style="font-size: 12px; font-weight: 500;">
						${runtime_info || 'N/A'}
					</div>
				</div>
			</div>

			${is_running ? `
				<div style="
					margin-top: 12px;
					padding: 8px 12px;
					background: rgba(255,255,255,0.15);
					border-left: 3px solid #10b981;
					border-radius: 4px;
					font-size: 11px;
					opacity: 0.9;
				">
					ℹ️ Clock is actively counting. Working days exclude weekends and public holidays.
				</div>
			` : `
				<div style="
					margin-top: 12px;
					padding: 8px 12px;
					background: rgba(255,255,255,0.15);
					border-left: 3px solid #f59e0b;
					border-radius: 4px;
					font-size: 11px;
					opacity: 0.9;
				">
					⚠️ Clock is paused. This period is excluded from working days calculation.
				</div>
			`}
		</div>
	`;

	// Insert at the top of the form
	frm.layout.wrapper.find('.statutory-clock-indicator').remove();
	$(clock_html).prependTo(frm.layout.wrapper.find('.form-layout'));
}

/**
 * Add summary dashboard at the top of the form
 */
function add_summary_dashboard(frm) {
	// Only show on saved documents
	if (frm.is_new()) return;

	// Get request details
	let request_link = frm.doc.request ? `<a href="/app/request/${frm.doc.request}">${frm.doc.request}</a>` : 'N/A';

	// Count affected parties and specialist reports
	const affected_parties_count = frm.doc.affected_parties ? frm.doc.affected_parties.length : 0;
	const approvals_count = frm.doc.written_approvals_obtained || 0;
	const specialist_reports_count = frm.doc.specialist_reports ? frm.doc.specialist_reports.length : 0;

	// Build proposal snapshot
	let proposal_items = [];
	if (frm.doc.building_height) proposal_items.push(`Height: ${frm.doc.building_height}m`);
	if (frm.doc.building_floor_area) proposal_items.push(`Floor Area: ${frm.doc.building_floor_area}m²`);
	if (frm.doc.earthworks_volume) proposal_items.push(`Earthworks: ${frm.doc.earthworks_volume}m³`);

	const proposal_summary = proposal_items.length > 0
		? proposal_items.join(' • ')
		: 'No dimensional data provided';

	const summary_html = `
		<div class="rc-summary-dashboard" style="
			background: #f8fafc;
			border: 1px solid #e2e8f0;
			border-radius: 8px;
			padding: 20px;
			margin-bottom: 20px;
			box-shadow: 0 1px 3px rgba(0,0,0,0.05);
		">
			<div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 15px;">
				📊 Application Summary
			</div>

			<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
				<!-- Request Details -->
				<div style="background: white; padding: 12px; border-radius: 6px; border-left: 3px solid #3b82f6;">
					<div style="font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Request</div>
					<div style="font-size: 14px; font-weight: 500; color: #1e293b;">${request_link}</div>
				</div>

				<!-- Consent Type -->
				<div style="background: white; padding: 12px; border-radius: 6px; border-left: 3px solid #8b5cf6;">
					<div style="font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Consent Type</div>
					<div style="font-size: 14px; font-weight: 500; color: #1e293b;">${frm.doc.consent_types || 'Not specified'}</div>
				</div>

				<!-- Activity Status -->
				<div style="background: white; padding: 12px; border-radius: 6px; border-left: 3px solid #ec4899;">
					<div style="font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Activity Status</div>
					<div style="font-size: 14px; font-weight: 500; color: #1e293b;">${frm.doc.activity_status || 'Not specified'}</div>
				</div>

				<!-- Notification Level -->
				<div style="background: white; padding: 12px; border-radius: 6px; border-left: 3px solid #f59e0b;">
					<div style="font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Notification</div>
					<div style="font-size: 14px; font-weight: 500; color: #1e293b;">${frm.doc.notification_level || 'Not Determined'}</div>
				</div>
			</div>

			<!-- Proposal Summary -->
			<div style="margin-top: 15px; padding: 12px; background: white; border-radius: 6px;">
				<div style="font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Proposal Details</div>
				<div style="font-size: 13px; color: #475569;">${proposal_summary}</div>
			</div>

			<!-- Metrics Row -->
			<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 15px;">
				<div style="background: white; padding: 10px; border-radius: 6px; text-align: center;">
					<div style="font-size: 24px; font-weight: 700; color: #3b82f6;">${affected_parties_count}</div>
					<div style="font-size: 11px; color: #64748b; margin-top: 3px;">Affected Parties</div>
				</div>
				<div style="background: white; padding: 10px; border-radius: 6px; text-align: center;">
					<div style="font-size: 24px; font-weight: 700; color: #10b981;">${approvals_count}</div>
					<div style="font-size: 11px; color: #64748b; margin-top: 3px;">Written Approvals</div>
				</div>
				<div style="background: white; padding: 10px; border-radius: 6px; text-align: center;">
					<div style="font-size: 24px; font-weight: 700; color: #8b5cf6;">${specialist_reports_count}</div>
					<div style="font-size: 11px; color: #64748b; margin-top: 3px;">Specialist Reports</div>
				</div>
				<div style="background: white; padding: 10px; border-radius: 6px; text-align: center;">
					<div style="font-size: 24px; font-weight: 700; color: ${frm.doc.iwi_consultation_undertaken ? '#10b981' : '#94a3b8'};">
						${frm.doc.iwi_consultation_undertaken ? '✓' : '—'}
					</div>
					<div style="font-size: 11px; color: #64748b; margin-top: 3px;">Iwi Consultation</div>
				</div>
			</div>
		</div>
	`;

	// Insert after clock indicator or at top
	frm.layout.wrapper.find('.rc-summary-dashboard').remove();
	const clock_indicator = frm.layout.wrapper.find('.statutory-clock-indicator');
	if (clock_indicator.length) {
		$(summary_html).insertAfter(clock_indicator);
	} else {
		$(summary_html).prependTo(frm.layout.wrapper.find('.form-layout'));
	}
}

/**
 * Enhance Request Information section with quick actions and styling
 */
function enhance_request_info_section(frm) {
	if (!frm.doc.request) return;

	// Style the Request Information section with blue background
	const request_info_section = frm.fields_dict['section_break_request_info'];
	if (request_info_section && request_info_section.wrapper) {
		$(request_info_section.wrapper).css({
			'background-color': '#eff6ff',
			'padding': '12px',
			'border-radius': '6px',
			'margin-top': '10px',
			'border-left': '4px solid #3b82f6'
		});

		// Add icon and quick action buttons to section header
		const section_head = $(request_info_section.wrapper).find('.section-head');
		if (section_head.length && !section_head.find('.request-info-actions').length) {
			// Add icon to label
			section_head.find('.section-title').prepend('🔗 ');

			// Add quick action buttons
			section_head.append(`
				<span class="request-info-actions" style="float: right; margin-left: 10px;">
					<button class="btn btn-xs btn-default"
						onclick="frappe.set_route('Form', 'Request', '${frm.doc.request}')"
						title="View full Request details">
						<svg class="icon icon-sm" style="width: 14px; height: 14px;">
							<use href="#icon-link"></use>
						</svg>
						View Request
					</button>
				</span>
			`);
		}

		// Add helper text if not already added
		if (!$(request_info_section.wrapper).find('.request-info-helper').length) {
			$(request_info_section.wrapper).find('.form-section').append(`
				<div class="request-info-helper" style="
					margin-top: 10px;
					padding: 8px 10px;
					background: rgba(59, 130, 246, 0.1);
					border-radius: 4px;
					font-size: 11px;
					color: #1e40af;
				">
					<svg class="icon icon-sm" style="width: 12px; height: 12px; vertical-align: middle;">
						<use href="#icon-info"></use>
					</svg>
					These details are synced from the parent Request and are read-only. To update, edit the <a href="/app/request/${frm.doc.request}" style="color: #2563eb; text-decoration: underline;">parent Request</a>.
				</div>
			`);
		}
	}

	// Style the Property Information subsection similarly
	const property_info_section = frm.fields_dict['section_break_property_info'];
	if (property_info_section && property_info_section.wrapper) {
		$(property_info_section.wrapper).css({
			'background-color': '#f0fdf4',
			'padding': '12px',
			'border-radius': '6px',
			'margin-top': '10px',
			'border-left': '4px solid #10b981'
		});

		// Add icon to label
		const prop_section_head = $(property_info_section.wrapper).find('.section-head');
		if (prop_section_head.length) {
			prop_section_head.find('.section-title').prepend('📍 ');
		}
	}

	// Add validation warning if Request not acknowledged
	if (frm.doc.request && !frm.layout.wrapper.find('.request-status-warning').length) {
		frappe.db.get_value('Request', frm.doc.request, 'status', (r) => {
			if (r && r.status !== 'Acknowledged' && r.status !== 'Processing' && r.status !== 'Approved') {
				const warning = $(`
					<div class="request-status-warning alert alert-warning" style="
						margin: 10px 0;
						padding: 10px 15px;
						background: #fef3c7;
						border: 1px solid #fbbf24;
						border-radius: 6px;
						font-size: 13px;
						color: #92400e;
					">
						<strong>⚠️ Request Status: ${r.status}</strong><br>
						<span style="font-size: 12px;">
							Resource Consent Applications are typically only processed after the Request has been acknowledged (s88 completeness check).
						</span>
					</div>
				`);
				warning.insertAfter(frm.fields_dict['section_break_property_info'].wrapper);
			}
		});
	}
}

/**
 * Style applicant-provided fields with visual distinction
 */
function style_applicant_fields(frm) {
	// List of applicant-provided fields
	const applicant_fields = [
		'consent_types', 'activity_status', 'assessment_of_effects', 'planning_assessment',
		'effects_on_people', 'physical_effects', 'ecosystem_effects', 'cultural_effects',
		'alternatives_considered', 'mitigation_proposed', 'affected_parties',
		'iwi_consultation_undertaken', 'iwi_consulted', 'cultural_impact_assessment',
		'specialist_reports', 'proposed_conditions', 'building_height', 'building_floor_area',
		'earthworks_volume', 'earthworks_vertical_alteration', 'vehicle_movements_daily',
		'parking_spaces_provided', 'hours_of_operation', 'consent_term_requested',
		'site_topography', 'existing_vegetation_description', 'watercourses_present',
		'watercourse_description', 'natural_hazards_identified', 'existing_infrastructure',
		'contamination_status_hail', 'earthworks_effects', 'discharge_contaminants_effects',
		'hazard_risk_assessment'
	];

	// Add subtle background color to applicant fields
	applicant_fields.forEach(fieldname => {
		const field = frm.fields_dict[fieldname];
		if (field && field.wrapper) {
			$(field.wrapper).css({
				'background-color': '#f0f9ff',
				'padding': '10px',
				'border-radius': '4px',
				'border-left': '3px solid #3b82f6'
			});

			// Add tooltip/label to indicate this is applicant-provided
			if (!$(field.wrapper).find('.applicant-field-label').length) {
				$(field.wrapper).prepend(`
					<div class="applicant-field-label" style="
						font-size: 10px;
						color: #3b82f6;
						text-transform: uppercase;
						margin-bottom: 5px;
						font-weight: 600;
					">📝 Applicant-Provided</div>
				`);
			}
		}
	});

	// Style council-only sections
	const council_sections = [
		'section_break_notification', 'section_break_hearing', 'section_break_decision',
		'section_break_statutory_clock'
	];

	council_sections.forEach(section_name => {
		const section = frm.fields_dict[section_name];
		if (section && section.wrapper) {
			$(section.wrapper).css({
				'background-color': '#fef3c7',
				'padding': '10px',
				'border-radius': '4px',
				'margin-top': '15px',
				'border-left': '3px solid #f59e0b'
			});

			if (!$(section.wrapper).find('.council-section-label').length) {
				$(section.wrapper).prepend(`
					<div class="council-section-label" style="
						font-size: 10px;
						color: #d97706;
						text-transform: uppercase;
						margin-bottom: 5px;
						font-weight: 600;
					">🏛️ Council-Only Section</div>
				`);
			}
		}
	});
}

/**
 * Make applicant fields read-only after request is submitted
 */
function make_applicant_fields_readonly(frm) {
	// Only make read-only if the linked request is submitted
	if (!frm.doc.request) return;

	frappe.db.get_value('Request', frm.doc.request, 'docstatus', (r) => {
		if (r && r.docstatus === 1) {
			// Request is submitted, lock applicant fields
			const applicant_fields = [
				'consent_types', 'activity_status', 'assessment_of_effects', 'planning_assessment',
				'effects_on_people', 'physical_effects', 'ecosystem_effects', 'cultural_effects',
				'alternatives_considered', 'mitigation_proposed', 'affected_parties',
				'iwi_consultation_undertaken', 'iwi_consulted', 'cultural_impact_assessment',
				'specialist_reports', 'proposed_conditions', 'building_height', 'building_floor_area',
				'earthworks_volume', 'earthworks_vertical_alteration', 'vehicle_movements_daily',
				'parking_spaces_provided', 'hours_of_operation', 'consent_term_requested',
				'site_topography', 'existing_vegetation_description', 'watercourses_present',
				'watercourse_description', 'natural_hazards_identified', 'existing_infrastructure',
				'contamination_status_hail', 'earthworks_effects', 'discharge_contaminants_effects',
				'hazard_risk_assessment'
			];

			applicant_fields.forEach(fieldname => {
				frm.set_df_property(fieldname, 'read_only', 1);
			});

			// Add a notice at the top
			if (!frm.layout.wrapper.find('.applicant-locked-notice').length) {
				const notice = $(`
					<div class="applicant-locked-notice" style="
						background: #fef3c7;
						border: 1px solid #fbbf24;
						border-radius: 6px;
						padding: 12px;
						margin-bottom: 15px;
						font-size: 13px;
						color: #92400e;
					">
						<strong>🔒 Applicant Fields Locked:</strong> The application has been submitted and applicant-provided fields are now read-only to prevent accidental modification.
					</div>
				`);
				notice.insertAfter(frm.layout.wrapper.find('.rc-summary-dashboard'));
			}
		}
	});
}

/**
 * Add custom action buttons
 */
function add_custom_buttons(frm) {
	if (frm.is_new()) return;

	// Prominent button to view linked request (main hub)
	if (frm.doc.request) {
		frm.add_custom_button(__('View Request (Main Hub)'), function() {
			frappe.set_route('Form', 'Request', frm.doc.request);
		}).addClass('btn-primary');

		// Add helpful message
		frm.dashboard.add_comment(
			__('Use the <strong>Request form</strong> to access Tasks, Meetings, Communications, and Assessment Project.'),
			'blue',
			true
		);
	}

	// Button to refresh condition templates
	frm.add_custom_button(__('Refresh Condition Templates'), function() {
		frappe.confirm(
			'This will clear existing conditions and reapply templates from the Request Type. Continue?',
			() => {
				frappe.call({
					method: 'lodgeick.lodgeick.doctype.resource_consent_application.resource_consent_application.refresh_condition_templates',
					args: {
						resource_consent_name: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frm.reload_doc();
						}
					}
				});
			}
		);
	}, __('Conditions'));

	// Button to start statutory clock
	if (!frm.doc.statutory_clock_started && !frm.is_new()) {
		frm.add_custom_button(__('Start Statutory Clock'), function() {
			frappe.confirm(
				'Start the RMA statutory timeframe clock for this application?',
				() => {
					frm.set_value('statutory_clock_started', frappe.datetime.now_datetime());
					frm.save();
				}
			);
		}, __('RMA Process'));
	}

	// Button to stop/resume clock
	if (frm.doc.statutory_clock_started) {
		if (frm.doc.statutory_clock_stopped) {
			frm.add_custom_button(__('Resume Clock'), function() {
				frappe.confirm(
					'Resume the statutory clock? (Information received from applicant)',
					() => {
						frm.set_value('statutory_clock_stopped', null);
						frm.save();
					}
				);
			}, __('RMA Process'));
		} else {
			frm.add_custom_button(__('Stop Clock (RFI)'), function() {
				frappe.confirm(
					'Stop the statutory clock? (Requesting further information from applicant)',
					() => {
						frm.set_value('statutory_clock_stopped', frappe.datetime.now_datetime());
						frm.save();
					}
				);
			}, __('RMA Process'));
		}
	}

	// Quick notification decision buttons
	if (!frm.doc.notification_level || frm.doc.notification_level === 'Not Determined') {
		frm.add_custom_button(__('Non-Notified'), function() {
			frm.set_value('notification_level', 'Non-Notified');
			frm.set_value('notification_determined_date', frappe.datetime.get_today());
			frm.save();
		}, __('Notification'));

		frm.add_custom_button(__('Limited Notified'), function() {
			frm.set_value('notification_level', 'Limited Notified');
			frm.set_value('notification_determined_date', frappe.datetime.get_today());
			frm.save();
		}, __('Notification'));

		frm.add_custom_button(__('Fully Notified'), function() {
			frm.set_value('notification_level', 'Fully Notified');
			frm.set_value('notification_determined_date', frappe.datetime.get_today());
			frm.save();
		}, __('Notification'));
	}
}

/**
 * Set up field visibility dependencies
 */
function setup_field_visibility(frm) {
	// Show/hide watercourse description based on checkbox
	frm.toggle_display('watercourse_description', frm.doc.watercourses_present);

	// Show/hide hearing details based on hearing required
	frm.toggle_display('hearing_date', frm.doc.hearing_required);
	frm.toggle_display('hearing_venue', frm.doc.hearing_required);
	frm.toggle_display('hearing_commissioners', frm.doc.hearing_required);
}

// Field-level events
frappe.ui.form.on('Resource Consent Application', {
	watercourses_present: function(frm) {
		frm.toggle_display('watercourse_description', frm.doc.watercourses_present);
	},

	hearing_required: function(frm) {
		frm.toggle_display('hearing_date', frm.doc.hearing_required);
		frm.toggle_display('hearing_venue', frm.doc.hearing_required);
		frm.toggle_display('hearing_commissioners', frm.doc.hearing_required);
	}
});
