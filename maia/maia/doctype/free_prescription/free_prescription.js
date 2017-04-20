// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia');


maia.FreePrescriptionController = frappe.ui.form.Controller.extend({

    refresh: function(frm) {
	if(!this.frm.doc.__islocal) {
	    this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print"));
	    this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print"));
	    this.frm.add_custom_button(__('Echography Prescription'), this.print_echo_prescription, __("Print"));
	}

    },

    print_drug_prescription: function(frm) {
    frappe.call({
	method:"maia.maia.print.print_prescription",
	args: {
	    "doctype": "Free Prescription",
	    "doc": cur_frm.doc.name,
	    "as_print": 1,
	    "print_format": "Drug Prescription"
	},
	callback: function(r) {
	    var new_window = window.open();
	    new_window.document.write(r.message);
	}
    })
    },

    print_lab_prescription: function(frm) {
    frappe.call({
	method:"maia.maia.print.print_prescription",
	args: {
	    "doctype": "Free Prescription",
	    "doc": cur_frm.doc.name,
	    "as_print": 1,
	    "print_format": "Lab Prescription"
	},
	callback: function(r) {
	    var new_window = window.open();
	    new_window.document.write(r.message);
	}
    })
    },

    print_echo_prescription: function(frm) {
    frappe.call({
	method:"maia.maia.print.print_prescription",
	args: {
	    "doctype": "Free Prescription",
	    "doc": cur_frm.doc.name,
	    "as_print": 1,
	    "print_format": "Echography Prescription"
	},
	callback: function(r) {
	    var new_window = window.open();
	    new_window.document.write(r.message);
	}
    })
    },

    set_default_print_format: function() {
	this.frm.meta.default_print_format = "Drug Prescription";
    }


});

$.extend(cur_frm.cscript, new maia.FreePrescriptionController({frm: cur_frm}));
