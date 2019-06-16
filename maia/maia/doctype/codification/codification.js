// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Codification', {
	refresh(frm) {
		if(!frm.doc.__islocal) {
			if(frm.doc.disabled == 1){
				frm.add_custom_button(__('Enable Code'), function() {
					enable_disable_codification(frm, 0);
				} );
			}
			else{
				frm.add_custom_button(__('Disable Code'), function() {
					enable_disable_codification(frm, 1);
				} );
			}
			
		}
	},

	codification(frm) {
		if(!frm.doc.codification_description) {
			frm.set_value("codification_description", frm.doc.codification);
		}
	}
})

const enable_disable_codification = (frm, val) => {
	frappe.call({
		method: "maia.maia.doctype.codification.codification.disable_enable_codification",
		args: {status: val, name: frm.doc.name},
		callback: function(r){
			frm.reload_doc();
		}
	});
}
