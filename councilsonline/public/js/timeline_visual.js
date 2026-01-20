/**
 * Timeline Visual Component
 *
 * Displays a visual timeline showing key milestones in the request lifecycle
 * Used on the Timeframes tab to show progress through key dates
 */

frappe.provide('councilsonline.timeline');

/**
 * Render timeline visual for Timeframes tab
 */
councilsonline.timeline.renderTimelineVisual = function(frm) {
	if (!frm || !frm.doc) {
		return '<p class="text-muted">No request data available</p>';
	}

	const milestones = [
		{
			key: 'submitted',
			label: 'Submitted',
			date: frm.doc.submitted_date,
			icon: 'upload',
			description: 'Request received and logged'
		},
		{
			key: 'acknowledged',
			label: 'Acknowledged',
			date: frm.doc.acknowledged_date,
			icon: 'eye',
			description: 'Request acknowledged, SLA clock started'
		},
		{
			key: 'target',
			label: 'Target Completion',
			date: frm.doc.target_completion_date,
			icon: 'flag',
			description: 'Statutory deadline for decision'
		},
		{
			key: 'actual',
			label: 'Actual Completion',
			date: frm.doc.actual_completion_date,
			icon: 'check-circle',
			description: 'Request completed'
		}
	];

	// Determine status for each milestone
	const today = frappe.datetime.now_date(true);

	const milestones_html = milestones.map((milestone, index) => {
		let status = 'pending';
		let date_display = 'Not set';
		let relative_time = '';

		if (milestone.date) {
			status = 'complete';
			date_display = frappe.datetime.str_to_user(milestone.date);

			// Calculate relative time
			const days_diff = frappe.datetime.get_day_diff(today, milestone.date);
			if (days_diff === 0) {
				relative_time = 'Today';
			} else if (days_diff === 1) {
				relative_time = 'Yesterday';
			} else if (days_diff === -1) {
				relative_time = 'Tomorrow';
			} else if (days_diff > 0) {
				relative_time = `${days_diff} days ago`;
			} else {
				relative_time = `In ${Math.abs(days_diff)} days`;
			}
		} else if (milestone.key === 'target' && index > 0 && milestones[index - 1].date) {
			// If target date is not set but previous milestone is, show as pending
			status = 'pending';
		}

		// Check if overdue
		if (milestone.key === 'target' && milestone.date && !frm.doc.actual_completion_date) {
			const days_remaining = frappe.datetime.get_day_diff(milestone.date, today);
			if (days_remaining < 0) {
				status = 'overdue';
				relative_time = `${Math.abs(days_remaining)} days overdue`;
			}
		}

		// Show connector between milestones (except for last one)
		const connector = index < milestones.length - 1 ? '<div class="milestone-connector"></div>' : '';

		return `
			<div class="milestone ${status}" data-milestone="${milestone.key}">
				<div class="milestone-icon">
					<i class="fa fa-${milestone.icon}"></i>
				</div>
				<div class="milestone-content">
					<strong>${milestone.label}</strong>
					<small class="milestone-date">${date_display}</small>
					${relative_time ? `<small class="milestone-relative">${relative_time}</small>` : ''}
					<small class="text-muted">${milestone.description}</small>
				</div>
				${connector}
			</div>
		`;
	}).join('');

	// Calculate processing metrics
	let processing_info = '';
	if (frm.doc.acknowledged_date) {
		const processing_days = frappe.datetime.get_day_diff(
			frm.doc.actual_completion_date || today,
			frm.doc.acknowledged_date
		);

		let days_to_deadline = '';
		if (frm.doc.target_completion_date && !frm.doc.actual_completion_date) {
			const remaining = frappe.datetime.get_day_diff(frm.doc.target_completion_date, today);
			days_to_deadline = `
				<div class="processing-metric">
					<span class="metric-label">Days to Deadline:</span>
					<span class="metric-value ${remaining < 0 ? 'text-danger' : remaining <= 5 ? 'text-warning' : 'text-success'}">
						${remaining < 0 ? `${Math.abs(remaining)} days overdue` : `${remaining} days remaining`}
					</span>
				</div>
			`;
		}

		processing_info = `
			<div class="processing-metrics">
				<h5><i class="fa fa-clock-o"></i> Processing Time</h5>
				<div class="processing-metric">
					<span class="metric-label">Days in Process:</span>
					<span class="metric-value">${processing_days} ${processing_days === 1 ? 'day' : 'days'}</span>
				</div>
				${days_to_deadline}
			</div>
		`;
	}

	return `
		<div class="timeline-visual">
			<div class="timeline-header">
				<h4><i class="fa fa-calendar"></i> Request Timeline</h4>
				<p class="text-muted">Track key dates and milestones</p>
			</div>
			<div class="timeline-milestones">
				${milestones_html}
			</div>
			${processing_info}
		</div>
	`;
};

/**
 * Get milestone status based on date and current state
 */
councilsonline.timeline.getMilestoneStatus = function(milestone_date, is_target, is_complete, current_date) {
	if (!milestone_date) {
		return 'pending';
	}

	if (is_complete) {
		return 'complete';
	}

	if (is_target && !is_complete) {
		const days_diff = frappe.datetime.get_day_diff(milestone_date, current_date);
		if (days_diff < 0) {
			return 'overdue';
		}
	}

	return 'complete';
};
