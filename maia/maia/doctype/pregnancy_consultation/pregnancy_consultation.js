// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide("maia");
{% include "maia/public/js/controllers/consultations.js" %}

frappe.ui.form.on('Pregnancy Consultation', {

})

maia.PregnancyConsultationController = frappe.ui.form.Controller.extend({

    onload: function(frm) {
	get_term_date(this.frm);
    },

    refresh: function(frm) {
	if(!this.frm.doc.__islocal) {
	    this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print"));
	    this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print"));
	    this.frm.add_custom_button(__('Echography Prescription'), this.print_echo_prescription, __("Print"));
	}

	get_term_date(this.frm);
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
    },

    print_echo_prescription: function(frm) {
    frappe.call({
	method:"maia.maia.print.print_prescription",
	args: {
	    "doctype": "Pregnancy Consultation",
	    "doc": cur_frm.doc.name,
	    "as_print": 1,
	    "print_format": "Echography Prescription"
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

var get_term_date = function(frm) {
    if (frm.doc.pregnancy_folder) {
	frappe.call({
	    "method": "frappe.client.get",
	    args: {
		doctype: "Pregnancy",
		name: frm.doc.pregnancy_folder
	    },
	    cache: false,
	    callback: function (data) {
		if (data.message) {
		    expected_term = data.message.expected_term;
		    beginning_of_pregnancy = data.message.beginning_of_pregnancy;
		    last_menstrual_period = data.message.last_menstrual_period;
		    consultation_date = frm.doc.consultation_date;

		    if (expected_term != null) {
			
			am_weeks = Math.floor((280 - frappe.datetime.get_diff(expected_term, consultation_date))/7)
			add_days = Math.floor(((280 - frappe.datetime.get_diff(expected_term, consultation_date))/7 - am_weeks) * 7)
			console.log("expected_term", expected_term, consultation_date)
		    }
		    else if (beginning_of_pregnancy != null) {
			am_weeks = Math.floor(frappe.datetime.get_diff(consultation_date, beginning_of_pregnancy)/7)
			add_days = Math.floor((frappe.datetime.get_diff(consultation_date, beginning_of_pregnancy)/7 - Math.floor(frappe.datetime.get_diff(consultation_date, beginning_of_pregnancy)/7))*7)
			console.log("beginning_pregancy", beginning_of_pregnancy, consultation_date)
		    }
		    else if (last_menstrual_period != null) {
			am_weeks = Math.floor(frappe.datetime.get_diff(consultation_date, last_menstrual_period)/7) + 2
			add_days = Math.floor((frappe.datetime.get_diff(consultation_date, last_menstrual_period)/7 - Math.floor(frappe.datetime.get_diff(consultation_date, last_menstrual_period)/7))*7)
		        console.log("last_menstrual", last_menstrual_period, consultation_date)

		    }
		   
		    
		    frappe.model.set_value(frm.doctype, frm.docname, "term", am_weeks + __(" Weeks Amenorrhea + ") + add_days + __(" Days"))
		}
	    }
	})
    } else {
	frappe.model.set_value(frm.doctype, frm.docname, "day", __("Please Set an Expected Term or Beginning of Pregnancy Date in the Pregnancy Folder"))
    }
};
