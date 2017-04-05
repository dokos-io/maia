// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide("maia");
{% include "maia/public/js/controllers/consultations.js" %}

frappe.ui.form.on('Pregnancy Consultation', {

})

maia.PregnancyConsultationController = frappe.ui.form.Controller.extend({

    refresh: function(frm) {
	if(!this.frm.doc.__islocal) {
	    this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print"));
	    this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print"));

	}
    },

    print_drug_prescription: function(frm) {
    frappe.call({
	method:"maia.maia.print.print_prescription",
	args: {
	    "doctype": "Pregnancy Consultation",
	    "doc": cur_frm.doc.name,
	    "as_print": 1,
	    "print_format": "Drug Prescription"
	},
	callback: function(r) {
	    var new_window = window.open();
	    new_window.document.write(r.message);
	    frappe.msgprint(r.message);
	}
    })
    },

    print_lab_prescription: function(frm) {
    frappe.call({
	method:"maia.maia.print.print_prescription",
	args: {
	    "doctype": "Pregnancy Consultation",
	    "doc": cur_frm.doc.name,
	    "as_print": 1,
	    "print_format": "Lab Prescription"
	},
	callback: function(r) {
	    var new_window = window.open();
	    new_window.document.write(r.message);
	    frappe.msgprint(r.message);
	}
    })
    }


});


$.extend(cur_frm.cscript, new maia.PregnancyConsultationController({frm: cur_frm}));