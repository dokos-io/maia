// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Revenue'] = {
	get_indicator: function(doc) {
		if (["Paid", "Unpaid"].includes(doc.status)) {
			return [__(doc.status), doc.status === "Paid" ? "green" : "orange"];
		}
	}
};