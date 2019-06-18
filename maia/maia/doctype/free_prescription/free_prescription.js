// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Free Prescription", {
	onload: function(frm) {
		if (frm.doc.docstatus != 1) {
			frappe.db.get_value("Professional Information Card", {user: frappe.session.user}, "name", r => {
				r && frm.set_value("practitioner", r.name);
			})
		}
	},

	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Drug Prescription'), () => { print_drug_prescription(frm) }, __("Print Prescription"));
			frm.add_custom_button(__('Lab Prescription'), () => { print_lab_prescription(frm) }, __("Print Prescription"));
			frm.add_custom_button(__('Echography Prescription'), () => { print_echo_prescription(frm) }, __("Print Prescription"));
		}
	}

});

{% include "maia/public/js/controllers/print_settings.js" %}
