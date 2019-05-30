// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia');
{% include "maia/public/js/controllers/consultations.js" %}

maia.EarlyPostnatalConsultationController = frappe.ui.form.Controller.extend({
	onload: function(frm) {
		if (this.frm.doc.docstatus != 1) {
			get_postdelivery_date(this.frm);
		}
		this.frm.fields_dict['pregnancy_folder'].get_query = function(doc) {
			return {
				filters: {
					"patient_record": doc.patient_record
				}
			}
		}
	},
	refresh: function(frm) {
		if (this.frm.doc.docstatus != 1) {
			get_postdelivery_date(this.frm);
		}
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

$.extend(cur_frm.cscript, new maia.EarlyPostnatalConsultationController({
	frm: cur_frm
}));

frappe.ui.form.on("Early Postnatal Consultation", {
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
	}
});

var get_postdelivery_date = function(frm) {
	if (frm.doc.pregnancy_folder) {
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Pregnancy",
				name: frm.doc.pregnancy_folder
			},
			cache: false,
			callback: function(data) {
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
