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

// Configure Gantt view for Project Task
frappe.views.GanttView = class ProjectTaskGanttView extends frappe.views.GanttView {
	get view_name() {
		return "Gantt";
	}

	setup_defaults() {
		super.setup_defaults();
		this.page_title = __("Project Tasks Gantt");
		this.fields = ["name", "title", "start_date", "due_date", "status", "priority", "assigned_to"];
	}

	get gantt_options() {
		return {
			...super.gantt_options,
			date_field: "start_date",
			end_date_field: "due_date",
			title_field: "title",
			bar_height: 30,
			padding: 18,
			view_mode: "Month",
			custom_popup_html: function(task) {
				const start_date = frappe.datetime.str_to_user(task.start_date || task.due_date);
				const end_date = frappe.datetime.str_to_user(task.due_date);
				const assigned_to = task.assigned_to || "Unassigned";

				return `
					<div class="gantt-task-popup">
						<h5>${task.title}</h5>
						<p><strong>Status:</strong> ${task.status}</p>
						<p><strong>Priority:</strong> ${task.priority || "Not Set"}</p>
						<p><strong>Start:</strong> ${start_date}</p>
						<p><strong>Due:</strong> ${end_date}</p>
						<p><strong>Assigned:</strong> ${assigned_to}</p>
					</div>
				`;
			}
		};
	}
};
