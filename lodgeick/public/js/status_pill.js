/**
 * Status Pill Component
 *
 * Renders color-coded status pills for workflow states
 * Used across Request forms and list views
 */

frappe.provide('lodgeick.status');

lodgeick.status.renderStatusPill = function(workflow_state) {
    if (!workflow_state) {
        return '<span class="text-muted">No Status</span>';
    }

    const statusConfig = {
        // Draft & Submission states
        'Draft': { color: 'gray', icon: 'edit', label: 'Draft' },
        'Submitted': { color: 'blue', icon: 'check', label: 'Submitted' },

        // Processing states
        'Acknowledged': { color: 'cyan', icon: 'eye', label: 'Acknowledged' },
        'Processing': { color: 'orange', icon: 'refresh', label: 'Processing' },

        // RFI (Request for Information) states
        'RFI Issued': { color: 'purple', icon: 'help', label: 'RFI Issued' },
        'RFI Received': { color: 'purple', icon: 'mail', label: 'RFI Received' },

        // Decision states
        'Pending Decision': { color: 'yellow', icon: 'clock', label: 'Pending Decision' },
        'Approved': { color: 'green', icon: 'check-circle', label: 'Approved' },
        'Approved with Conditions': { color: 'green', icon: 'alert-circle', label: 'Approved (Conditions)' },
        'Declined': { color: 'red', icon: 'x-circle', label: 'Declined' },

        // Terminal states
        'Withdrawn': { color: 'gray', icon: 'arrow-left', label: 'Withdrawn' },
        'Cancelled': { color: 'gray', icon: 'x', label: 'Cancelled' },
        'Completed': { color: 'green', icon: 'check-circle', label: 'Completed' },

        // Building Consent specific states
        'Awaiting Inspection': { color: 'blue', icon: 'search', label: 'Awaiting Inspection' },
        'Inspections Complete': { color: 'green', icon: 'check', label: 'Inspections Complete' },
        'CCC Issued': { color: 'green', icon: 'award', label: 'CCC Issued' },

        // Task states (if used in Request context)
        'Assigned': { color: 'blue', icon: 'user', label: 'Assigned' },
        'In Progress': { color: 'orange', icon: 'activity', label: 'In Progress' },
        'Resolved': { color: 'green', icon: 'check', label: 'Resolved' },
        'Closed': { color: 'gray', icon: 'archive', label: 'Closed' },
        'Escalated': { color: 'red', icon: 'alert-triangle', label: 'Escalated' },

        // Appeal state
        'Under Appeal': { color: 'orange', icon: 'repeat', label: 'Under Appeal' }
    };

    const config = statusConfig[workflow_state] || {
        color: 'gray',
        icon: 'circle',
        label: workflow_state
    };

    return `
        <div class="status-pill status-${config.color}"
             role="status"
             aria-label="Request status: ${config.label}"
             title="${config.label}">
            <i class="fa fa-${config.icon}" aria-hidden="true"></i>
            <span>${config.label}</span>
        </div>
    `;
}

/**
 * Get status color class for use in other components
 */
lodgeick.status.getStatusColor = function(workflow_state) {
    const colorMap = {
        'Draft': 'gray',
        'Submitted': 'blue',
        'Acknowledged': 'cyan',
        'Processing': 'orange',
        'RFI Issued': 'purple',
        'RFI Received': 'purple',
        'Pending Decision': 'yellow',
        'Approved': 'green',
        'Approved with Conditions': 'green',
        'Declined': 'red',
        'Withdrawn': 'gray',
        'Cancelled': 'gray',
        'Completed': 'green',
        'Awaiting Inspection': 'blue',
        'Inspections Complete': 'green',
        'CCC Issued': 'green',
        'Assigned': 'blue',
        'In Progress': 'orange',
        'Resolved': 'green',
        'Closed': 'gray',
        'Escalated': 'red',
        'Under Appeal': 'orange'
    };

    return colorMap[workflow_state] || 'gray';
}

/**
 * Render compact status badge (for list views)
 */
lodgeick.status.renderStatusBadge = function(workflow_state) {
    const color = lodgeick.status.getStatusColor(workflow_state);
    return `<span class="badge badge-${color}">${workflow_state}</span>`;
};
