// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

{% include "maia/public/js/controllers/consultations.js" %}

frappe.ui.form.on("Early Postnatal Consultation", {
	onload: function(frm) {
		if (frm.doc.docstatus != 1) {
			frm.trigger("get_postdelivery_date");
		}
		frm.fields_dict['pregnancy_folder'].get_query = function(doc) {
			return {
				filters: {
					"patient_record": doc.patient_record
				}
			}
		}
	},
	refresh: function(frm) {
		if (frm.doc.docstatus != 1) {
			frm.trigger("get_postdelivery_date");
		}
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Drug Prescription'), () => { print_drug_prescription(frm) }, __("Print Prescription"));
			frm.add_custom_button(__('Lab Prescription'), () => { print_lab_prescription(frm) }, __("Print Prescription"));
			frm.add_custom_button(__('Echography Prescription'), () => { print_echo_prescription(frm) }, __("Print Prescription"));
		}
	},
	weight_of_the_day: function(frm) {
		if (frm.doc.weight_of_the_day && frm.doc.pregnancy_folder) {
			frappe.call({
				method: "maia.maia.doctype.early_postnatal_consultation.early_postnatal_consultation.get_last_weight",
				args: {
					consultation: frm.doc.name,
					pregnancy: frm.doc.pregnancy_folder,
					child: 'firstchild'
				},
				callback: function(r) {
					if (r.message) {
						let daily_weight = frm.doc.weight_of_the_day;
						let difference = daily_weight - r.message;
						frappe.model.set_value('Early Postnatal Consultation', frm.doc.name, 'weight_gain', difference)
					}
				}
			})
		}
	},
	weight_of_the_day_2: function(frm) {
			if (frm.doc.weight_of_the_day_2 && frm.doc.pregnancy_folder) {
				frappe.call({
					method: "maia.maia.doctype.early_postnatal_consultation.early_postnatal_consultation.get_last_weight",
					args: {
						consultation: frm.doc.name,
						pregnancy: frm.doc.pregnancy_folder,
						child: 'secondchild'
					},
					callback: function(r) {
						if (r.message) {
							let daily_weight = frm.doc.weight_of_the_day_2;
							let difference = daily_weight - r.message;
							frappe.model.set_value('Early Postnatal Consultation', frm.doc.name, 'weight_gain_2', difference)
						}
					}
				})
			}
	},
	weight_of_the_day_3: function(frm) {
			if (frm.doc.weight_of_the_day_3 && frm.doc.pregnancy_folder) {
				frappe.call({
					method: "maia.maia.doctype.early_postnatal_consultation.early_postnatal_consultation.get_last_weight",
					args: {
						consultation: frm.doc.name,
						pregnancy: frm.doc.pregnancy_folder,
						child: 'thirdchild'
					},
					callback: function(r) {
						if (r.message) {
							let daily_weight = frm.doc.weight_of_the_day_3;
							let difference = daily_weight - r.message;
							frappe.model.set_value('Early Postnatal Consultation', frm.doc.name, 'weight_gain_3', difference)
						}
					}
				})
			}
	},
	pregnancy_folder: function(frm) {
		if (frm.doc.pregnancy_folder) {
			frappe.call({
					method: 'frappe.client.get',
					args: {
						doctype: 'Pregnancy',
						name: frm.doc.pregnancy_folder
					},
			}).then((r) => {
				if (r.message) {
						frappe.model.set_value("Early Postnatal Consultation", frm.doc.name, "twins", r.message.twins);
						frappe.model.set_value("Early Postnatal Consultation", frm.doc.name, "triplets", r.message.triplets);
						frappe.model.set_value("Early Postnatal Consultation", frm.doc.name, "newborn_fullname", r.message.full_name);
						frappe.model.set_value("Early Postnatal Consultation", frm.doc.name, "newborn_fullname_2", r.message.full_name_2);
						frappe.model.set_value("Early Postnatal Consultation", frm.doc.name, "newborn_fullname_3", r.message.full_name_3);
				}
			});
		}
	},
	get_postdelivery_date: function(frm) {
		if (frm.doc.pregnancy_folder) {
			frappe.db.get_value("Pregnancy", frm.doc.pregnancy_folder, "date_time", e => {
				const calculated_day = frappe.datetime.get_diff(frm.doc.consultation_date, e.date_time) + 1;
				if (calculated_day) {
					frm.set_value("day", __("D +") + " " + calculated_day)
				} else {
					frm.set_value("day", __("Please add the delivery datetime in the Pregnancy folder"))
				}
			})
		} else {
			frm.set_value("day", __("Please Select a Pregnancy Folder"))
		}
	}
})
