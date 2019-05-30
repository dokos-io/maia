// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia');

frappe.ui.form.on('Perineum Rehabilitation', {
		refresh: function(frm) {
			cur_frm.toggle_display("patient_name", (cur_frm.doc.patient_name && cur_frm.doc.patient_name!==cur_frm.doc.patient));
			cur_frm.add_fetch('patient_record', 'patient_name', 'patient_name');
			render_sports(frm);
		}
});

const render_sports = frm => {
	if(frm.fields_dict['sports_before_pregnancy']) {
		frappe.xcall("maia.maia.doctype.perineum_rehabilitation.perineum_rehabilitation.get_patient_sports", {patient: frm.doc.patient_record})
		.then(e => { 
			$(frm.fields_dict['sports_before_pregnancy'].wrapper)
			.html(frappe.render_template("sports_before_pregnancy", {data: e}))
		 })

	}
}

{% include "maia/public/js/controllers/folders.js" %}
{% include "maia/public/js/controllers/print_settings.js" %}
