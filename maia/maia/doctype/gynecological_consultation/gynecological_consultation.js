// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.provide ("maia.maia");

{% include "maia/public/js/controllers/consultations.js" %}

maia.maia.GynecologicalConsultation = frappe.ui.form.Controller.extend({
    refresh: function() {
	if(!cur_frm.doc.__islocal) {
	    cur_frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print"));
	    cur_frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print"));
	    cur_frm.page.set_inner_btn_group_as_primary(__("Print"));
	}
    }

    /*print_drug_prescription: function() {

    }

    print_lab_prescription: function() {

    }*/

});

$.extend(cur_frm.cscript, new maia.maia.GynecologicalConsultation({frm: cur_frm}));
