// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia');


maia.FreePrescriptionController = frappe.ui.form.Controller.extend({

  refresh: function(frm) {
    if (!this.frm.doc.__islocal) {
      this.frm.add_custom_button(__('Drug Prescription'), this.print_drug_prescription, __("Print"));
      this.frm.add_custom_button(__('Lab Prescription'), this.print_lab_prescription, __("Print"));
      this.frm.add_custom_button(__('Echography Prescription'), this.print_echo_prescription, __("Print"));
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
