// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on(this.frm.doctype, {
	onload: function(frm) {
		if(frm.doc.__islocal) {
			if(frm.doc.practitioner) {
				var arg = {practitioner: frm.doc.practitioner}
			} else {
				var arg = {user: frappe.session.user}
			}
			frappe.call({
				method: "maia.maia.utils.get_letter_head",
				args: arg,
				callback: function(r) {
					frm.set_value("letter_head", r.message);
				}
			});
		}
	}
});
