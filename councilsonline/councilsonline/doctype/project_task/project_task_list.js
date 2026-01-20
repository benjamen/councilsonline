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
