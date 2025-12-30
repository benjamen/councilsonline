// Copyright (c) 2025, Optified and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Task", {
	refresh(frm) {
		// Auto-set start_date to today if not set
		if (!frm.doc.start_date) {
			frm.set_value('start_date', frappe.datetime.get_today());
		}
	}
});

// Configure Project Task list view with Gantt support
if (frappe.views.ListView) {
	frappe.listview_settings['Project Task'] = {
		add_fields: ["status", "priority", "assigned_to", "start_date", "due_date"],
		get_indicator: function(doc) {
			if (doc.status === "Completed") {
				return [__("Completed"), "green", "status,=,Completed"];
			} else if (doc.status === "In Progress") {
				return [__("In Progress"), "blue", "status,=,In Progress"];
			} else if (doc.status === "Cancelled") {
				return [__("Cancelled"), "gray", "status,=,Cancelled"];
			} else {
				return [__("Open"), "orange", "status,=,Open"];
			}
		}
	};
}
