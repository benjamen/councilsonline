/**
 * Universal Summary Dashboard
 *
 * Reusable dashboard component for displaying request metrics.
 * Configurable for different request types with custom metrics.
 */

import { getLinkedDocumentCount } from './action_bar_utils.js';

/**
 * Create a summary dashboard above the form
 * @param {Object} frm - Frappe form object
 * @param {Object} config - Dashboard configuration
 * @param {string} config.api_method - API method to fetch summary data
 * @param {Array} config.metrics - Array of metric configurations
 * @param {string} config.color - Dashboard background color (default: purple gradient)
 */
export function createSummaryDashboard(frm, config = {}) {
	const default_config = {
		api_method: 'lodgeick.api.get_request_summary_data',
		color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
		metrics: [
			{
				label: 'Tasks',
				field: 'tasks_count',
				icon: 'check-square',
				color: '#3498db'
			},
			{
				label: 'Meetings',
				field: 'meetings_count',
				icon: 'calendar',
				color: '#9b59b6'
			},
			{
				label: 'Communications',
				field: 'communications_count',
				icon: 'message-square',
				color: '#e74c3c'
			},
			{
				label: 'Assessment Status',
				field: 'assessment_status',
				icon: 'award',
				color: '#27ae60',
				is_status: true
			}
		]
	};

	const dashboard_config = { ...default_config, ...config };

	// Remove existing dashboard if present
	frm.dashboard.wrapper.find('.request-summary-dashboard').remove();

	// Fetch dashboard data
	frappe.call({
		method: dashboard_config.api_method,
		args: {
			request_id: frm.doc.name
		},
		callback: function(r) {
			if (r.message) {
				renderDashboard(frm, dashboard_config, r.message);
			}
		}
	});
}

/**
 * Render the dashboard HTML
 * @param {Object} frm - Frappe form object
 * @param {Object} config - Dashboard configuration
 * @param {Object} data - Dashboard data from API
 */
function renderDashboard(frm, config, data) {
	const metrics_html = config.metrics.map(metric => {
		const value = data[metric.field] || (metric.is_status ? 'Not Started' : 0);
		const display_value = metric.is_status ? value : `<strong>${value}</strong>`;

		return `
			<div class="dashboard-metric" style="flex: 1; text-align: center; padding: 10px;">
				<div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-bottom: 5px;">
					<svg class="icon icon-sm" style="width: 16px; height: 16px; margin-right: 5px; vertical-align: middle;">
						<use href="#icon-${metric.icon}"></use>
					</svg>
					${metric.label}
				</div>
				<div style="font-size: ${metric.is_status ? '16px' : '24px'}; color: white; font-weight: ${metric.is_status ? 'normal' : 'bold'};">
					${display_value}
				</div>
			</div>
		`;
	}).join('<div style="width: 1px; background: rgba(255,255,255,0.2); margin: 10px 0;"></div>');

	const dashboard_html = `
		<div class="request-summary-dashboard" style="
			background: ${config.color};
			padding: 15px 20px;
			margin: -15px -15px 15px -15px;
			border-radius: 5px;
			color: white;
			box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		">
			<div style="display: flex; align-items: center; justify-content: space-between;">
				${metrics_html}
			</div>
		</div>
	`;

	frm.dashboard.wrapper.prepend(dashboard_html);
}

/**
 * Create a simple count dashboard without API call
 * @param {Object} frm - Frappe form object
 * @param {Array} count_configs - Array of {label, doctype, icon, color}
 */
export async function createSimpleCountDashboard(frm, count_configs) {
	const counts = {};

	// Fetch all counts in parallel
	await Promise.all(
		count_configs.map(async (cfg) => {
			counts[cfg.doctype] = await getLinkedDocumentCount(frm.doc.name, cfg.doctype);
		})
	);

	// Build metrics from counts
	const metrics = count_configs.map(cfg => ({
		label: cfg.label,
		field: cfg.doctype,
		icon: cfg.icon || 'file',
		color: cfg.color || '#3498db',
		is_status: false
	}));

	// Create dashboard data
	const data = {};
	count_configs.forEach(cfg => {
		data[cfg.doctype] = counts[cfg.doctype];
	});

	renderDashboard(frm, { metrics }, data);
}

/**
 * Update a specific metric in the dashboard
 * @param {Object} frm - Frappe form object
 * @param {string} metric_label - Label of metric to update
 * @param {string|number} new_value - New value to display
 */
export function updateDashboardMetric(frm, metric_label, new_value) {
	const dashboard = frm.dashboard.wrapper.find('.request-summary-dashboard');
	if (dashboard.length) {
		const metrics = dashboard.find('.dashboard-metric');
		metrics.each(function() {
			const label = $(this).find('div').first().text().trim();
			if (label.includes(metric_label)) {
				$(this).find('div').last().html(`<strong>${new_value}</strong>`);
			}
		});
	}
}

/**
 * Create custom metric card
 * @param {string} label - Metric label
 * @param {string|number} value - Metric value
 * @param {string} icon - Feather icon name
 * @param {string} color - Text color
 * @returns {string} HTML for metric card
 */
export function createMetricCard(label, value, icon, color = 'white') {
	return `
		<div class="dashboard-metric" style="flex: 1; text-align: center; padding: 10px;">
			<div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-bottom: 5px;">
				<svg class="icon icon-sm" style="width: 16px; height: 16px; margin-right: 5px; vertical-align: middle;">
					<use href="#icon-${icon}"></use>
				</svg>
				${label}
			</div>
			<div style="font-size: 24px; color: ${color}; font-weight: bold;">
				${value}
			</div>
		</div>
	`;
}
