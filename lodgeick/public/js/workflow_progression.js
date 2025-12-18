/**
 * Workflow Progression Component
 *
 * Displays a visual stepper showing the current position in the workflow
 * Type-aware: Different flows for Resource Consent, Building Consent, SPISC, LIM
 */

frappe.provide('lodgeick.workflow');

/**
 * Get workflow steps based on request type
 */
lodgeick.workflow.getWorkflowSteps = function(request_type, request_category) {
    // Define workflow steps for different request types
    const workflows = {
        'Resource Consent': [
            { key: 'Draft', label: 'Draft', icon: 'edit' },
            { key: 'Submitted', label: 'Submitted', icon: 'check' },
            { key: 'Acknowledged', label: 'Acknowledged', icon: 'eye' },
            { key: 'Processing', label: 'Processing', icon: 'refresh' },
            { key: 'Pending Decision', label: 'Decision', icon: 'gavel' },
            { key: 'Approved', label: 'Approved', icon: 'check-circle' },
            { key: 'Completed', label: 'Completed', icon: 'flag' }
        ],
        'Building Consent': [
            { key: 'Draft', label: 'Draft', icon: 'edit' },
            { key: 'Submitted', label: 'Submitted', icon: 'check' },
            { key: 'Acknowledged', label: 'Acknowledged', icon: 'eye' },
            { key: 'Processing', label: 'Processing', icon: 'refresh' },
            { key: 'Approved', label: 'Approved', icon: 'check-circle' },
            { key: 'Awaiting Inspection', label: 'Inspections', icon: 'search' },
            { key: 'CCC Issued', label: 'CCC', icon: 'award' },
            { key: 'Completed', label: 'Completed', icon: 'flag' }
        ],
        'LIM': [
            { key: 'Draft', label: 'Draft', icon: 'edit' },
            { key: 'Submitted', label: 'Submitted', icon: 'check' },
            { key: 'Acknowledged', label: 'Acknowledged', icon: 'eye' },
            { key: 'Processing', label: 'Processing', icon: 'refresh' },
            { key: 'Completed', label: 'Completed', icon: 'flag' }
        ],
        'SPISC': [
            { key: 'Draft', label: 'Draft', icon: 'edit' },
            { key: 'Submitted', label: 'Submitted', icon: 'check' },
            { key: 'Acknowledged', label: 'Acknowledged', icon: 'eye' },
            { key: 'Processing', label: 'Assessment', icon: 'clipboard' },
            { key: 'Approved', label: 'Approved', icon: 'check-circle' },
            { key: 'Completed', label: 'Completed', icon: 'flag' }
        ],
        'default': [
            { key: 'Draft', label: 'Draft', icon: 'edit' },
            { key: 'Submitted', label: 'Submitted', icon: 'check' },
            { key: 'Acknowledged', label: 'Acknowledged', icon: 'eye' },
            { key: 'Processing', label: 'Processing', icon: 'refresh' },
            { key: 'Completed', label: 'Completed', icon: 'flag' }
        ]
    };

    // Try to match by request_type first, then request_category, then default
    let workflow_key = 'default';

    if (request_type) {
        // Direct match
        if (workflows[request_type]) {
            workflow_key = request_type;
        }
        // Partial match (e.g., "Resource Consent - Subdivision" matches "Resource Consent")
        else {
            for (let key in workflows) {
                if (request_type.includes(key)) {
                    workflow_key = key;
                    break;
                }
            }
        }
    } else if (request_category && workflows[request_category]) {
        workflow_key = request_category;
    }

    return workflows[workflow_key];
};

/**
 * Determine the state of each workflow step
 */
lodgeick.workflow.getStepState = function(step_key, current_state, all_steps) {
    // Terminal states that indicate completion outside normal flow
    const terminal_states = ['Declined', 'Withdrawn', 'Cancelled'];
    const approval_states = ['Approved', 'Approved with Conditions'];

    // If current state is terminal, mark all as completed up to the terminal state
    if (terminal_states.includes(current_state)) {
        return step_key === 'Completed' ? 'pending' : 'completed';
    }

    // Handle approval variations
    if (approval_states.includes(current_state) && step_key === 'Approved') {
        return 'active';
    }

    // Find current step index
    const current_index = all_steps.findIndex(s => s.key === current_state || approval_states.includes(current_state) && s.key === 'Approved');
    const step_index = all_steps.findIndex(s => s.key === step_key);

    if (step_index === -1) return 'pending';

    if (step_index < current_index) {
        return 'completed';
    } else if (step_index === current_index || (approval_states.includes(current_state) && step_key === 'Approved')) {
        return 'active';
    } else {
        return 'pending';
    }
};

/**
 * Render workflow progression bar
 */
lodgeick.workflow.renderWorkflowProgression = function(workflow_state, request_type, request_category) {
    if (!workflow_state) {
        return '<p class="text-muted">No workflow state</p>';
    }

    const steps = lodgeick.workflow.getWorkflowSteps(request_type, request_category);
    const completed_count = steps.filter(step => lodgeick.workflow.getStepState(step.key, workflow_state, steps) === 'completed').length;
    const progress_percentage = (completed_count / steps.length) * 100;

    const steps_html = steps.map((step, index) => {
        const state = lodgeick.workflow.getStepState(step.key, workflow_state, steps);
        const is_last = index === steps.length - 1;

        return `
            <div class="workflow-step ${state}" data-step="${step.key}">
                <div class="workflow-step-icon" title="${step.key}">
                    ${state === 'completed' ? '<i class="fa fa-check"></i>' :
                      state === 'active' ? '<i class="fa fa-' + step.icon + '"></i>' :
                      (index + 1)}
                </div>
                <div class="workflow-step-label">${step.label}</div>
            </div>
        `;
    }).join('');

    return `
        <div class="workflow-progression-bar" role="navigation" aria-label="Workflow progression">
            <div class="workflow-connector">
                <div class="workflow-connector-progress" style="width: ${progress_percentage}%"></div>
            </div>
            ${steps_html}
        </div>
    `;
};

/**
 * Render compact workflow indicator (for dashboards)
 */
lodgeick.workflow.renderWorkflowIndicator = function(workflow_state, request_type, request_category) {
    const steps = lodgeick.workflow.getWorkflowSteps(request_type, request_category);
    const current_index = steps.findIndex(s => s.key === workflow_state);
    const total = steps.length;

    if (current_index === -1) {
        return `<span class="text-muted">Step 0 of ${total}</span>`;
    }

    return `
        <div class="workflow-indicator">
            <strong>Step ${current_index + 1} of ${total}</strong>
            <div class="progress" style="height: 4px; margin-top: 4px;">
                <div class="progress-bar bg-primary" role="progressbar"
                     style="width: ${((current_index + 1) / total) * 100}%"
                     aria-valuenow="${current_index + 1}"
                     aria-valuemin="0"
                     aria-valuemax="${total}">
                </div>
            </div>
        </div>
    `;
};

/**
 * Get next workflow step
 */
lodgeick.workflow.getNextStep = function(workflow_state, request_type, request_category) {
    const steps = lodgeick.workflow.getWorkflowSteps(request_type, request_category);
    const current_index = steps.findIndex(s => s.key === workflow_state);

    if (current_index === -1 || current_index === steps.length - 1) {
        return null;
    }

    return steps[current_index + 1];
};

/**
 * Get previous workflow step
 */
lodgeick.workflow.getPreviousStep = function(workflow_state, request_type, request_category) {
    const steps = lodgeick.workflow.getWorkflowSteps(request_type, request_category);
    const current_index = steps.findIndex(s => s.key === workflow_state);

    if (current_index <= 0) {
        return null;
    }

    return steps[current_index - 1];
};
