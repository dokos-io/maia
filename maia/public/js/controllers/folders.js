// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on(this.frm.doctype, {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			add_buttons(frm);
		}
	}
})

let add_buttons = function(frm) {
	frappe.db.get_list('Maia Standard Letter', {filters:{'doc_type': frm.doctype, 'disabled': 0}, fields: ["name"]}).then(result => {
		if (result) {
			frm.page.set_inner_btn_group_as_primary(__("Print a Standard Letter"));
			result.forEach(value => {
				frm.add_custom_button(__(value.name), function() {
					var w = window.open(
						frappe.urllib.get_full_url("/api/method/maia.maia.print.download_standard_letter_pdf?"
							+ "doctype=" + encodeURIComponent(frm.doctype)
							+ "&name=" + encodeURIComponent(frm.doc.name)
							+ "&template=" + encodeURIComponent(value.name)
					));
					if (!w) {
						frappe.msgprint(__("Please enable pop-ups")); return;
					}
				}, __("Print a Standard Letter"))
			})
		}
		
	});    
}


