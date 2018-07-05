// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide("maia");
{% include "maia/public/js/controllers/consultations.js" %}

frappe.ui.form.on('Pregnancy Consultation', {
	 weight: function(frm) {
		 if (frm.doc.weight && frm.doc.patient_record) {
			 frappe.call({
				 method: "maia.maia.doctype.pregnancy_consultation.pregnancy_consultation.get_comparison_weight",
				 args: {
					 patient_record: frm.doc.patient_record
				 },
				 callback: function(r) {
					 if (r.message) {
						 let daily_weight = frm.doc.weight;
						 let base_difference = "Non Comparable";
						 let latest_difference = "Non Comparable";
						 if (r.message.base_weight != 0) {
							 base_difference = daily_weight - r.message.base_weight;
						 }

						 if (r.message.last_weight != 0) {
							 latest_difference = daily_weight - r.message.last_weight;
						 }
						 frappe.model.set_value('Pregnancy Consultation', frm.doc.name, 'weight_gain', base_difference)
						 frappe.model.set_value('Pregnancy Consultation', frm.doc.name, 'latest_weight_gain', latest_difference)
					 }
				 }
			 })
		 }
	 },
	 pregnancy_folder: function(frm) {
		 get_term_date(frm);
	 }
})

maia.PregnancyConsultationController = frappe.ui.form.Controller.extend({

	onload: function(frm) {
		if(this.frm.doc.docstatus!=1) {
			get_term_date(this.frm);
		}

		this.frm.fields_dict['pregnancy_folder'].get_query = function(doc) {
			return {
				filters: {
					"patient_record": doc.patient_record
				}
			}
		}

	},
	consultation_date: function(frm) {
		get_term_date(this.frm);
	},
	refresh: function(frm) {
		if (!this.frm.doc.__islocal) {
			this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print Prescription"));
			this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print Prescription"));
			this.frm.add_custom_button(__('Echography Prescription'), this.print_echo_prescription, __("Print Prescription"));
		}
		if(this.frm.doc.docstatus!=1) {
		 get_term_date(this.frm)
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
	},

	set_default_print_format: function() {
		this.frm.meta.default_print_format = "";
	}

});
$.extend(this.frm.cscript, new maia.PregnancyConsultationController({
	frm: this.frm
}));


var get_term_date = function(frm) {
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
					let expected_term = data.message.expected_term;
					let beginning_of_pregnancy = data.message.beginning_of_pregnancy;
					let last_menstrual_period = data.message.last_menstrual_period;
					let consultation_date = frm.doc.consultation_date;

					if (beginning_of_pregnancy != null) {
						am_weeks = Math.floor(frappe.datetime.get_diff(consultation_date, beginning_of_pregnancy) / 7) + 2
						add_days = Math.floor((frappe.datetime.get_diff(consultation_date, beginning_of_pregnancy) / 7 - Math.floor(frappe.datetime.get_diff(consultation_date, beginning_of_pregnancy) / 7)) * 7)
						frappe.model.set_value(frm.doctype, frm.docname, "term", am_weeks + " " + __("Weeks Amenorrhea +") + " " + add_days + " " + __("Days"))

					} else if (expected_term != null) {
						am_weeks = Math.floor((287 - frappe.datetime.get_diff(expected_term, consultation_date)) / 7)
						add_days = Math.floor(((287 - frappe.datetime.get_diff(expected_term, consultation_date)) / 7 - am_weeks) * 7)
						frappe.model.set_value(frm.doctype, frm.docname, "term", am_weeks + " " + __("Weeks Amenorrhea +") + " " + add_days + " " + __("Days"))

					} else if (last_menstrual_period != null) {
						am_weeks = Math.floor(frappe.datetime.get_diff(consultation_date, last_menstrual_period) / 7)
						add_days = Math.floor((frappe.datetime.get_diff(consultation_date, last_menstrual_period) / 7 - Math.floor(frappe.datetime.get_diff(consultation_date, last_menstrual_period) / 7)) * 7)
						frappe.model.set_value(frm.doctype, frm.docname, "term", am_weeks + " " + __("Weeks Amenorrhea +") + " " + add_days + " " + __("Days"))

					} else {

						frappe.model.set_value(frm.doctype, frm.docname, "term", "");
					}
				}
			}
		})
	} else {
		frappe.model.set_value(frm.doctype, frm.docname, "day", __("Please Set an Expected Term or Beginning of Pregnancy Date in the Pregnancy Folder"))
	}
};
