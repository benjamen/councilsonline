// Copyright (c) 2025, Optified and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assessment Project", {
	refresh(frm) {
		// Add Gantt Chart button
		if (!frm.is_new()) {
			frm.add_custom_button(__('Gantt Chart'), function() {
				frappe.route_options = {
					"assessment_project": frm.doc.name
				};
				frappe.set_route("List", "Project Task", "Gantt");
			}, __("View"));

			// Add Tasks List button
			frm.add_custom_button(__('Tasks List'), function() {
				frappe.route_options = {
					"assessment_project": frm.doc.name
				};
				frappe.set_route("List", "Project Task");
			}, __("View"));
		}
	}
});
