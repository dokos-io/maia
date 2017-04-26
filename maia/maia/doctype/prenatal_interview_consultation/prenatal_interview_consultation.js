// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide('maia');

{% include "maia/public/js/controllers/consultations.js" %}

frappe.ui.form.on('Prenatal Interview Consultation', {
	refresh: function(frm) {

	}
});


maia.PrenatalInterviewConsultationController = frappe.ui.form.Controller.extend({

    onload: function(frm) {
	this.frm.fields_dict['prenatal_interview_folder'].get_query = function(doc) {
	    return {
		filters: {
		    "patient_record": doc.patient_record
		}
	    }
	}
    }
});

$.extend(this.frm.cscript, new maia.PrenatalInterviewConsultationController({frm: this.frm}));
