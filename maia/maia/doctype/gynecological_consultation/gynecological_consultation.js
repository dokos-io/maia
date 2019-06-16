// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

{% include "maia/public/js/controllers/consultations.js" %}

frappe.ui.form.on("Gynecological Consultation", {
	onload: function(frm) {
		frm.fields_dict['gynecological_folder'].get_query = function(doc) {
			return {
				filters: {
					"patient_record": doc.patient_record
				}
			}
		}
	},
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Drug Prescription'), () => { print_drug_prescription(frm) }, __("Print Prescription"));
			frm.add_custom_button(__('Lab Prescription'), () => { print_lab_prescription(frm) }, __("Print Prescription"));
			frm.add_custom_button(__('Echography Prescription'), () => { print_echo_prescription(frm) }, __("Print Prescription"));
		}
	},
	weight: function(frm) {
		const weight = frm.doc.weight;
		frappe.db.get_value("Patient Record", {'name': frm.doc.patient_record}, 'height', (data) => {
			if (data.height) {
				const bmi = Math.round(frm.doc.weight / Math.pow(data.height, 2));
				frm.set_value("body_mass_index", bmi);
			}
		});
	}
})
