// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on('Pregnancy', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on('Lab Exam Results', {
	exam_type: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.db.get_value('Lab Exam Type', {name: row.exam_type}, 'default_value', (r) => {
				frappe.model.set_value(cdt, cdn, "show_on_dashboard", r.default_value);
		});
	}
});
