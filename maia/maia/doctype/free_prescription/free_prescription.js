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
