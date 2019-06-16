// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on(this.frm.doctype, {
	onload: function(frm) {
		if(frm.doc.__islocal) {
			if(frm.doc.practitioner) {
				var arg = {practitioner: frm.doc.practitioner}
			} else {
				var arg = {user: frappe.session.user}
			}
			frappe.call({
				method: "maia.maia.utils.get_letter_head",
				args: arg,
				callback: function(r) {
					frm.set_value("letter_head", r.message);
				}
			});
		}
	},

	lab_exam_template(frm) {
		if(frm.doc.lab_exam_template) {
			frappe.call({
				"method": "maia.maia.doctype.lab_exam_template.lab_exam_template.get_lab_exam_template",
				args: {
					lab_exam_template: frm.doc.lab_exam_template
				},
				callback: function (data) {
						$.each(data.message || [], function(i, v){
							let d = frappe.model.add_child(frm.doc, "Lab Exam Prescription", "lab_prescription_table");
							d.lab_exam = v.exam_type;
							d.additional_notes = v.additional_notes;
						});
						refresh_field("lab_prescription_table");
				}
			});
		}
	},

	drug_list_template(frm) {
		if(frm.doc.drug_list_template) {
			frappe.call({
				"method": "maia.maia.doctype.drug_list_template.drug_list_template.get_drug_list_template",
				args: {
					drug_list_template: frm.doc.drug_list_template
				},
				callback: function (data) {
						$.each(data.message || [], function(i, v){
							let d = frappe.model.add_child(frm.doc, "Drug Prescription", "drug_prescription_table");
							d.drug = v.drug;
							d.posology = v.posology;
							d.pharmaceutical_form = v.pharmaceutical_form;
							d.treatment_duration = v.treatment_duration;
							d.additional_notes = v.additional_notes;
						});
						refresh_field("drug_prescription_table");
				}
			});
		}
	}
});

const print_drug_prescription = (frm) => {
	var w = window.open(
		frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
			"doctype=" + encodeURIComponent(frm.doc.doctype) +
			"&name=" + encodeURIComponent(frm.doc.name) +
			"&format=Drug Prescription" +
			"&no_letterhead=0" +
			"&_lang=fr")
	);
	if (!w) {
		frappe.msgprint(__("Please enable pop-ups"));
		return;
	}
}

const print_lab_prescription = (frm) => {
	var w = window.open(
		frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
			"doctype=" + encodeURIComponent(frm.doc.doctype) +
			"&name=" + encodeURIComponent(frm.doc.name) +
			"&format=Lab Prescription" +
			"&no_letterhead=0" +
			"&_lang=fr")
	);
	if (!w) {
		frappe.msgprint(__("Please enable pop-ups"));
		return;
	}
}

const print_echo_prescription = (frm) => {
	var w = window.open(
		frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
			"doctype=" + encodeURIComponent(frm.doc.doctype) +
			"&name=" + encodeURIComponent(frm.doc.name) +
			"&format=Echography Prescription" +
			"&no_letterhead=0" +
			"&_lang=fr")
	);
	if (!w) {
		frappe.msgprint(__("Please enable pop-ups"));
		return;
	}
}