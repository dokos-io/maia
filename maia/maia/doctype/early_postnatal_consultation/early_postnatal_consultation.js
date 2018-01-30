// Copyright (c) 2017, DOKOS and contributors
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
  }

});

$.extend(cur_frm.cscript, new maia.EarlyPostnatalConsultationController({
  frm: cur_frm
}));

frappe.ui.form.on("Early Postnatal Consultation", "pregnancy_folder", function(frm) {
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
