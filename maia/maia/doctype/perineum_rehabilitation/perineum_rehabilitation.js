// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia');

frappe.ui.form.on('Perineum Rehabilitation', {
    refresh: function(frm) {
	cur_frm.toggle_display("patient_name",
			       (cur_frm.doc.patient_name && cur_frm.doc.patient_name!==cur_frm.doc.patient));

	cur_frm.add_fetch('patient_record', 'patient_name', 'patient_name');

    }


});

maia.PatientController = frappe.ui.form.Controller.extend({

});

$.extend(cur_frm.cscript, new maia.PatientController({frm: cur_frm}));
