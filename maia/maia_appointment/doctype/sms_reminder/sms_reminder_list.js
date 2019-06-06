// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// See license.txt

// render
frappe.listview_settings['SMS Reminder'] = {
	get_indicator: function(doc) {
		return [__(doc.status), doc.status === "Queued" ? "orange" : ("Sent" ? "green" : "red")];
	}
};