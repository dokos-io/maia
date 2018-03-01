// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide('maia');

{% include "maia/public/js/controllers/consultations.js" %}

maia.PostNatalConsultationController = frappe.ui.form.Controller.extend({

  onload: function(frm) {
    this.frm.fields_dict['pregnancy_folder'].get_query = function(doc) {
      return {
        filters: {
          "patient_record": doc.patient_record
        }
      }
    }

  },
	refresh: function(frm) {
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
  },
	set_default_print_format: function() {
    this.frm.meta.default_print_format = "";
  }
});
$.extend(this.frm.cscript, new maia.PostNatalConsultationController({
  frm: this.frm
}));
