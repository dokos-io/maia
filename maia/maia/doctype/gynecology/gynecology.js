// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

maia.GynecologyController = frappe.ui.form.Controller.extend({

    onload: function(frm) {
	get_first_menses_and_regular_cycles(this.frm);
    },

    refresh: function(frm) {
	get_first_menses_and_regular_cycles(this.frm);
    },
    
});

$.extend(this.frm.cscript, new maia.GynecologyController({frm: this.frm}));


var get_first_menses_and_regular_cycles = function(frm) {
    if (frm.doc.patient) {
	frappe.call({
	    "method": "frappe.client.get",
	    args: {
		doctype: "Patient",
		name: frm.doc.patient
	    },
	    cache: false,
	    callback: function (data) {
		if (data.message) {
		    first_menses = data.message.first_menses;
		    regular_cycles = data.message.regular_cycles;


		    if (first_menses != null && regular_cycles != null) {
			frappe.model.set_value(frm.doctype, frm.docname, "first_menses", first_menses);
			frappe.model.set_value(frm.doctype, frm.docname, "regular_cycles", regular_cycles);
		    } else if (first_menses != null && regular_cycles == null) {
			frappe.model.set_value(frm.doctype, frm.docname, "first_menses", first_menses);
			frappe.model.set_value(frm.doctype, frm.docname, "regular_cycles", "");
		    } else if (first_menses == null && regular_cyles != null) {
			frappe.model.set_value(frm.doctype, frm.docname, "first_menses", "");
			frappe.model.set_value(frm.doctype, frm.docname, "regular_cycles", regular_cycles);
		    } else {
			frappe.model.set_value(frm.doctype, frm.docname, "first_menses", "");
			frappe.model.set_value(frm.doctype, frm.docname, "regular_cycles", "");
		    }
			
		}
	    }
	})	
    }
};

