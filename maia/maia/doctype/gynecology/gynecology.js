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
    if (frm.doc.patient_record) {
	frappe.call({
	    "method": "frappe.client.get",
	    args: {
		doctype: "Patient Record",
		name: frm.doc.patient_record
	    },
	    cache: false,
	    callback: function (data) {
		if (data.message) {
		    first_menses = data.message.first_menses;
		    regular_cycles = data.message.regular_cycles;
		    contraception = data.message.contraception;

		 
		    frappe.model.set_value(frm.doctype, frm.docname, "first_menses", first_menses); 
		    frappe.model.set_value(frm.doctype, frm.docname, "regular_cycles", regular_cycles);
		    frappe.model.set_value(frm.doctype, frm.docname, "contraception", contraception);

		}
	    }
	})
    }
};
