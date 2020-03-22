// Copyright (c) 2020, Dokos SAS
// License: See license.txt

frappe.ui.form.on("Address", {
	refresh: function(frm) {
		if(frm.doc.__islocal) {
			const last_doc = frappe.contacts.get_last_doc(frm);
			if(frappe.dynamic_link && frappe.dynamic_link.doc
					&& frappe.dynamic_link.doc.name == last_doc.docname) {
                frm.set_value("address_title", `${last_doc.docname}-${__(frm.doc.address_type)}`);
			}
        }
    },
    address_type: function(frm) {
        if (frm.doc.links) {
			if (frm.doc.links[0].link_doctype && frm.doc.links[0].link_name) {
                frm.set_value("address_title", `${frm.doc.links[0].link_name}-${__(frm.doc.address_type)}`);
            }
        }
    }
})

frappe.ui.form.on('Dynamic Link', {
	link_name(frm, cdt, cdn) {
        const row = locals[cdt][cdn]
        if (row.link_doctype && row.link_name) {
            frm.set_value("address_title", `${row.link_name}-${__(frm.doc.address_type)}`);
        }
    }
});