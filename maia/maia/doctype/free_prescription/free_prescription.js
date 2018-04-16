// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia');

frappe.ui.form.on(this.frm.doctype, {
	onload: function(frm) {
	if (frm.doc.docstatus != 1) {
		frappe.call({
				"method": "maia.client.get_practitioner",
				args: {
					doctype: "Professional Information Card",
					filters: {
						user: frappe.session.user
					},
					fieldname: "name"
				},
				cache: false,
				callback: function(data) {
					if (!data.exe && data.message) {
						frappe.model.set_value(frm.doctype, frm.docname, "practitioner", data.message.name)
					}
				}
			})
		}
	},
	lab_exam_template: function(frm) {
		if(frm.doc.lab_exam_template) {
			frappe.call({
				"method": "maia.maia.doctype.lab_exam_template.lab_exam_template.get_lab_exam_template",
				args: {
					lab_exam_template: frm.doc.lab_exam_template
				},
				callback: function (data) {
						$.each(data.message || [], function(i, v){
							var d = frappe.model.add_child(frm.doc, "Lab Exam Prescription", "lab_prescription_table");
							d.lab_exam = v.exam_type;
						});
						refresh_field("lab_prescription_table");
				}
			});
		}
	},
	drug_list_template: function(frm) {
		if(frm.doc.drug_list_template) {
			frappe.call({
				"method": "maia.maia.doctype.drug_list_template.drug_list_template.get_drug_list_template",
				args: {
					drug_list_template: frm.doc.drug_list_template
				},
				callback: function (data) {
						$.each(data.message || [], function(i, v){
							var d = frappe.model.add_child(frm.doc, "Drug Prescription", "drug_prescription_table");
							d.drug = v.drug;
							d.posology = v.posology;
							d.pharmaceutical_form = v.pharmaceutical_form;
						});
						refresh_field("drug_prescription_table");
				}
			});
		}
	}

});

maia.FreePrescriptionController = frappe.ui.form.Controller.extend({

	refresh: function(frm) {
		if (!this.frm.doc.__islocal) {
			this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print Prescription"));
			this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print Prescription"));
			this.frm.add_custom_button(__('Echography Prescription'), this.print_echo_prescription, __("Print Prescription"));
		}

	},

	print_drug_prescription: function(frm) {
		var w = window.open(
			frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
				"doctype=" + encodeURIComponent(cur_frm.doc.doctype) +
				"&name=" + encodeURIComponent(cur_frm.doc.name) +
				"&format=Drug Prescription" +
				"&no_letterhead=0" +
				"&_lang=fr")
		);
		if (!w) {
			frappe.msgprint(__("Please enable pop-ups"));
			return;
		}
	},

	print_lab_prescription: function(frm) {
		var w = window.open(
			frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
				"doctype=" + encodeURIComponent(cur_frm.doc.doctype) +
				"&name=" + encodeURIComponent(cur_frm.doc.name) +
				"&format=Lab Prescription" +
				"&no_letterhead=0" +
				"&_lang=fr")
		);
		if (!w) {
			frappe.msgprint(__("Please enable pop-ups"));
			return;
		}
	},

	print_echo_prescription: function(frm) {
		var w = window.open(
			frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
				"doctype=" + encodeURIComponent(cur_frm.doc.doctype) +
				"&name=" + encodeURIComponent(cur_frm.doc.name) +
				"&format=Echography Prescription" +
				"&no_letterhead=0" +
				"&_lang=fr")
		);
		if (!w) {
			frappe.msgprint(__("Please enable pop-ups"));
			return;
		}
	}

});

$.extend(cur_frm.cscript, new maia.FreePrescriptionController({
	frm: cur_frm
}));

{% include "maia/public/js/controllers/print_settings.js" %}
