// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maia Fiscal Year', {
	onload(frm) {
		if(frm.doc.__islocal) {
			frm.set_value("year_start_date",
				frappe.datetime.add_days(frappe.defaults.get_default("year_end_date"), 1));
		}
	},
	refresh(frm) {
		frm.toggle_enable('year_start_date', doc.__islocal)
		frm.toggle_enable('year_end_date', doc.__islocal)
	},
	year_start_date(frm) {
		const year_end_date =
			frappe.datetime.add_days(frappe.datetime.add_months(frm.doc.year_start_date, 12), -1);
		frm.set_value("year_end_date", year_end_date);
	},
});
