// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide ('maia');
{% include "maia/public/js/controllers/consultations.js" %}

maia.EarlyPostnatalConsultationController = frappe.ui.form.Controller.extend({
    onload: function(frm) {
	get_postdelivery_date(this.frm);
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
		    today = frappe.datetime.str_to_obj(frappe.datetime.get_today()).getDate();
		    delivery_date = frappe.datetime.str_to_obj(data.message.date_time).getDate();
		    calculated_day = today - delivery_date;
		    console.log(today, delivery_date, calculated_day);
		    frappe.model.set_value(frm.doctype, frm.docname, "day", "J + " + calculated_day)
		}
	    }
	})
    } else {
	frappe.model.set_value(frm.doctype, frm.docname, "day", __("Please Select a Pregnancy Folder"))
    }
};
