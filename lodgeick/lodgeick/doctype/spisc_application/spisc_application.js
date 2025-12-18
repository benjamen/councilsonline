// Copyright (c) 2025, Optified and contributors
// For license information, please see license.txt

/**
 * SPISC Application Form Script
 *
 * SPISC-specific functionality only.
 * For common actions (Tasks, Meetings, Communications, Assessment Project),
 * use the Request form which has the universal action bar.
 */

frappe.ui.form.on('SPISC Application', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			// Add quick link to parent Request
			add_view_request_button(frm);

			// Add SPISC-specific eligibility assessment button
			add_eligibility_assessment_button(frm);

			// Visual enhancements for SPISC fields
			enhance_spisc_sections(frm);

			// Display age calculation
			display_age_info(frm);
		}
	},

	birth_date: function(frm) {
		// Auto-calculate age when birth date changes
		if (frm.doc.birth_date) {
			calculate_and_display_age(frm);
		}
	},

	monthly_income: function(frm) {
		// Show warning if income exceeds threshold
		check_income_threshold(frm);
	}
});


/**
 * Add prominent "View Request" button to navigate to parent Request
 */
function add_view_request_button(frm) {
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
}


/**
 * Add SPISC-specific eligibility assessment button
 */
function add_eligibility_assessment_button(frm) {
	if (frm.doc.docstatus === 1 && !frm.doc.eligibility_status) {
		frm.add_custom_button(__('Assess Eligibility'), function() {
			assess_spisc_eligibility(frm);
		}, __('SPISC Actions'));
	}

	// Show eligibility status if already assessed
	if (frm.doc.eligibility_status && frm.doc.eligibility_status !== 'Pending') {
		const indicator = frm.doc.eligibility_status === 'Eligible' ? 'green' : 'red';
		frm.dashboard.set_headline_alert(
			__('Eligibility Status: {0}', [frm.doc.eligibility_status]),
			indicator
		);
	}
}


/**
 * Assess SPISC eligibility using backend method
 */
function assess_spisc_eligibility(frm) {
	frappe.call({
		method: 'lodgeick.lodgeick.doctype.spisc_application.spisc_application.assess_eligibility',
		args: {
			name: frm.doc.name
		},
		freeze: true,
		freeze_message: __('Assessing eligibility...'),
		callback: function(r) {
			if (r.message) {
				frappe.msgprint({
					title: __('Eligibility Assessed'),
					message: __('Eligibility status: {0}', [r.message.eligibility_status]),
					indicator: r.message.eligibility_status === 'Eligible' ? 'green' : 'orange'
				});
				frm.reload_doc();
			}
		}
	});
}


/**
 * Enhance SPISC-specific form sections with visual styling
 */
function enhance_spisc_sections(frm) {
	// Highlight important eligibility fields
	const eligibility_fields = ['age', 'birth_date', 'monthly_income', 'income_source'];

	eligibility_fields.forEach(field => {
		if (frm.fields_dict[field]) {
			const field_wrapper = frm.fields_dict[field].$wrapper;
			field_wrapper.find('.control-label').css('font-weight', 'bold');
		}
	});

	// Add visual indicator for age requirement
	if (frm.doc.age) {
		const age_field = frm.fields_dict.age;
		if (age_field) {
			const meets_requirement = frm.doc.age >= 60;
			const color = meets_requirement ? '#27ae60' : '#e74c3c';
			age_field.$wrapper.find('.control-value').css({
				'color': color,
				'font-weight': 'bold',
				'font-size': '1.1em'
			});
		}
	}
}


/**
 * Display age information prominently
 */
function display_age_info(frm) {
	if (frm.doc.age) {
		const meets_requirement = frm.doc.age >= 60;
		const message = meets_requirement
			? __('Age Requirement Met: {0} years old', [frm.doc.age])
			: __('Age Requirement NOT Met: {0} years old (must be 60+)', [frm.doc.age]);

		const indicator = meets_requirement ? 'green' : 'red';

		frm.dashboard.add_indicator(message, indicator);
	}
}


/**
 * Calculate and display age based on birth date
 */
function calculate_and_display_age(frm) {
	if (!frm.doc.birth_date) return;

	const today = new Date();
	const birth_date = new Date(frm.doc.birth_date);

	let age = today.getFullYear() - birth_date.getFullYear();
	const month_diff = today.getMonth() - birth_date.getMonth();

	if (month_diff < 0 || (month_diff === 0 && today.getDate() < birth_date.getDate())) {
		age--;
	}

	// Update the age field display (backend will set it on save)
	if (age !== frm.doc.age) {
		frappe.show_alert({
			message: __('Calculated age: {0} years', [age]),
			indicator: age >= 60 ? 'green' : 'orange'
		});
	}
}


/**
 * Check income threshold and show warning if exceeded
 */
function check_income_threshold(frm) {
	const POVERTY_THRESHOLD = 10000; // PHP 10,000 per month

	if (frm.doc.monthly_income && frm.doc.monthly_income > POVERTY_THRESHOLD) {
		frappe.msgprint({
			title: __('Income Threshold Warning'),
			message: __(
				'Monthly income (PHP {0}) exceeds the poverty threshold (PHP {1}). ' +
				'This may affect eligibility for Social Pension.',
				[frm.doc.monthly_income.toLocaleString(), POVERTY_THRESHOLD.toLocaleString()]
			),
			indicator: 'orange'
		});
	}
}
