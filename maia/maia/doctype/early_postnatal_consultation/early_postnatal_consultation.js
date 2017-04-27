// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide ('maia');
{% include "maia/public/js/controllers/consultations.js" %}

maia.EarlyPostnatalConsultationController = frappe.ui.form.Controller.extend({
    onload: function(frm) {
	get_postdelivery_date(this.frm);
	this.frm.fields_dict['pregnancy_folder'].get_query = function(doc) {
	    return {
		filters: {
		    "patient_record": doc.patient_record
		}
	    }
	}
    },

    refresh: function(frm) {
	get_postdelivery_date(this.frm);
    }

});

$.extend(cur_frm.cscript, new maia.EarlyPostnatalConsultationController({frm: cur_frm}));

var get_postdelivery_date = function(frm) {
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
		    consultation_date = frm.doc.consultation_date;
		    delivery_date = data.message.date_time;
		    calculated_day = frappe.datetime.get_diff(consultation_date, delivery_date) + 1;
		 
		    frappe.model.set_value(frm.doctype, frm.docname, "day", __("D + ") + calculated_day)
		}
	    }
	})
    } else {
	frappe.model.set_value(frm.doctype, frm.docname, "day", __("Please Select a Pregnancy Folder"))
    }
};
