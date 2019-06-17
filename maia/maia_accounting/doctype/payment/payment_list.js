// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// See license.txt

// render
frappe.listview_settings['Payment'] = {
	get_indicator: function(doc) {
		if (["Unreconciled", "Reconciled"].includes(doc.status)) {
			return [__(doc.status), doc.status === "Reconciled" ? "green" : "orange"];
		}
	}
};