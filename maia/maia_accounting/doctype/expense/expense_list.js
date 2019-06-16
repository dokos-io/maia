// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// See license.txt

// render
frappe.listview_settings['Expense'] = {
	get_indicator: function(doc) {
		if (["Paid", "Unpaid"].includes(doc.status)) {
			return [__(doc.status), doc.status === "Paid" ? "green" : "orange"];
		}
	}
};