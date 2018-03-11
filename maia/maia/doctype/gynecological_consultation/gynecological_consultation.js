// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.provide("maia.maia");

{% include "maia/public/js/controllers/consultations.js" %}

maia.maia.GynecologicalConsultation = frappe.ui.form.Controller.extend({
  onload: function(frm) {
    this.frm.fields_dict['gynecological_folder'].get_query = function(doc) {
      return {
        filters: {
          "patient_record": doc.patient_record
        }
      }
    }

  },

  refresh: function() {
    if (!this.frm.doc.__islocal) {
      this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print Prescription"));
      this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print Prescription"));
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
  }
});

$.extend(cur_frm.cscript, new maia.maia.GynecologicalConsultation({
  frm: cur_frm
}));

frappe.ui.form.on("Gynecological Consultation", "weight", function(frm) {
  var weight = frm.doc.weight;
  frappe.db.get_value("Patient Record", {'name': frm.doc.patient_record}, 'height', (data) => {
		if (data.height) {
			bmi = Math.round(weight / Math.pow(data.height, 2));
			frappe.model.set_value(frm.doctype, frm.docname, "body_mass_index", bmi)
		}
	});
});
