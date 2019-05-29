// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt
frappe.ui.form.on(this.frm.doctype, {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			add_buttons(frm);
		}
	}
})

let add_buttons = function(frm) {
	frm.page.add_menu_item(__("Letter"), function() {
		frm.create_letter();
	}, false); 
}


