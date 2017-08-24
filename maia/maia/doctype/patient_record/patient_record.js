// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide("maia");

maia.PatientRecordController = frappe.ui.form.Controller.extend({
    
    refresh: function() {
	frappe.dynamic_link = {doc: this.frm.doc, fieldname: 'name', doctype: 'Patient Record'};

	if(this.frm.doc.__islocal){
	    hide_field(['address_html']);
	    frappe.contacts.clear_address_and_contact(this.frm);
	}
	else {
	    unhide_field(['address_html']);
	    frappe.contacts.render_address_and_contact(this.frm);
	    erpnext.utils.set_party_dashboard_indicators(cur_frm);
	}

    }
});

$.extend(cur_frm.cscript, new maia.PatientRecordController({frm: cur_frm}));

frappe.ui.form.on("Patient Record", {
    invite_as_user: function(frm) {
	frm.save();
	var d = new frappe.ui.Dialog({
	    'title': __('Create a New Website User ?'),
	    fields: [
		{ fieldtype:"HTML", options:__("Are you certain you want to create a website user for this patient ?") },
		{ fieldname: 'ok_button', fieldtype: 'Button', label: __("Yes") },
	    ]
	});
	d.show();
	d.fields_dict.ok_button.input.onclick = function () {
	    return frappe.call({
		method: "maia.maia.doctype.patient_record.patient_record.invite_user",
		args: {
		    contact: frm.doc.name
		},
		callback: function(r) {
		    frm.set_value("website_user", r.message);
		    frm.save();
		    d.hide();
		}
	    });
	};
    }
});

frappe.ui.form.on("Patient Record", "patient_date_of_birth", function(frm) {

	today = new Date();
	birthDate = new Date(frm.doc.patient_date_of_birth);
	if(today < birthDate){
	    frappe.msgprint(__('Please select a valid Date'));
	    frappe.model.set_value(frm.doctype,frm.docname, "patient_date_of_birth", null)
	}else{
	    age_yr = today.getFullYear() - birthDate.getFullYear();
	    today_m = today.getMonth()+1 //Month jan = 0
	    birth_m = birthDate.getMonth()+1 //Month jan = 0
	    m = today_m - birth_m;

	    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
		age_yr--;
	    }

	    age_str = null
	    if(age_yr > 0)
		age_str = age_yr+ " " + __('Years Old')

	    frappe.model.set_value(frm.doctype,frm.docname, "patient_age", age_str)
    }
});

frappe.ui.form.on("Patient Record", "spouse_date_of_birth", function(frm) {

	today = new Date();
	birthDate = new Date(frm.doc.spouse_date_of_birth);
	if(today < birthDate){
	    frappe.msgprint(__('Please select a valid Date'));
	    frappe.model.set_value(frm.doctype,frm.docname, "spouse_date_of_birth", null)
	}else{
	    age_yr = today.getFullYear() - birthDate.getFullYear();
	    today_m = today.getMonth()+1 //Month jan = 0
	    birth_m = birthDate.getMonth()+1 //Month jan = 0
	    m = today_m - birth_m;

	    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
		age_yr--;
	    }

	    age_str = null
	    if(age_yr > 0)
		age_str = age_yr+ " " + __('Years Old')

	    frappe.model.set_value(frm.doctype,frm.docname, "spouse_age", age_str)
    }
});

frappe.ui.form.on("Patient Record", "height", function(frm) {

    var weight = frm.doc.weight;
    var height = frm.doc.height;
    bmi = Math.round(weight / Math.pow(height, 2));
    frappe.model.set_value(frm.doctype,frm.docname, "body_mass_index", bmi)

});

frappe.ui.form.on("Patient Record", "weight", function(frm) {

    var weight = frm.doc.weight;
    var height = frm.doc.height;
    bmi = Math.round(weight / Math.pow(height, 2));
    frappe.model.set_value(frm.doctype,frm.docname, "body_mass_index", bmi)

});
