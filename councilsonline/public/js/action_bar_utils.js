/**
 * Universal Action Bar Utilities
 *
 * Reusable functions for action bars across all request types.
 * Provides consistent UX for Tasks, Meetings, Communications, and Assessment Projects.
 */

frappe.provide('councilsonline.actionBar');

/**
 * View linked documents in list view filtered by request
 * @param {Object} frm - Frappe form object
 * @param {string} doctype - DocType to view (e.g., 'Project Task', 'Council Meeting')
 */
councilsonline.actionBar.viewLinkedDocuments = function(frm, doctype) {
	frappe.route_options = {
		"request": frm.doc.name
	};
	frappe.set_route("List", doctype);
};

/**
 * Open the Assessment Project linked to this request
 * @param {Object} frm - Frappe form object
 */
councilsonline.actionBar.openAssessmentProject = function(frm) {
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
};

/**
 * Create a new linked document with default values
 * @param {Object} frm - Frappe form object
 * @param {string} doctype - DocType to create
 * @param {Object} defaults - Default field values
 */
councilsonline.actionBar.createLinkedDocument = function(frm, doctype, defaults = {}) {
	const doc_defaults = {
		request: frm.doc.name,
		...defaults
	};

	frappe.new_doc(doctype, doc_defaults);
};

/**
 * Show dialog to send notification to requester
 * @param {Object} frm - Frappe form object
 */
councilsonline.actionBar.showSendNotificationDialog = function(frm) {
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
				method: 'councilsonline.api.send_request_notification',
				args: {
					request_id: frm.doc.name,
					subject: values.subject,
					message: values.message,
					channel: values.channel
				},
				callback: function(r) {
					if (r.message) {
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
};

/**
 * Show dialog to add internal note to request
 * @param {Object} frm - Frappe form object
 */
councilsonline.actionBar.showAddInternalNoteDialog = function(frm) {
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
				method: 'councilsonline.api.add_internal_note',
				args: {
					request_id: frm.doc.name,
					note: values.note,
					visibility: values.visibility
				},
				callback: function(r) {
					if (r.message) {
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
};

/**
 * Create quick action button for creating linked document
 * @param {Object} frm - Frappe form object
 * @param {string} label - Button label
 * @param {string} doctype - DocType to create
 * @param {Object} defaults - Default field values
 * @param {string} group - Button group name
 */
councilsonline.actionBar.addCreateButton = function(frm, label, doctype, defaults, group) {
	frm.add_custom_button(__(label),
		() => councilsonline.actionBar.createLinkedDocument(frm, doctype, defaults),
		__(group)
	);
};

/**
 * Create quick action button for viewing linked documents
 * @param {Object} frm - Frappe form object
 * @param {string} label - Button label
 * @param {string} doctype - DocType to view
 * @param {string} group - Button group name
 */
councilsonline.actionBar.addViewButton = function(frm, label, doctype, group) {
	frm.add_custom_button(__(label),
		() => councilsonline.actionBar.viewLinkedDocuments(frm, doctype),
		__(group)
	);
};

/**
 * Get count of linked documents for dashboard
 * @param {string} request_id - Request ID
 * @param {string} doctype - DocType to count
 * @returns {Promise<number>} Count of linked documents
 */
councilsonline.actionBar.getLinkedDocumentCount = async function(request_id, doctype) {
	return new Promise((resolve, reject) => {
		frappe.call({
			method: 'frappe.client.get_count',
			args: {
				doctype: doctype,
				filters: { request: request_id }
			},
			callback: function(r) {
				if (r.message !== undefined) {
					resolve(r.message);
				} else {
					reject('Failed to get count');
				}
			}
		});
	});
};
