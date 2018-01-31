// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide("maia.patient_record");

frappe.ui.form.on("Patient Record", {
  onload: function(frm) {
    frm.set_query("website_user", function() {
      return {
        query: "maia.maia.doctype.patient_record.patient_record.get_users_for_website"
      }
    });
    frm.trigger("setup_chart");
  },
  refresh: function(frm) {
    frappe.dynamic_link = {
      doc: frm.doc,
      fieldname: 'name',
      doctype: 'Patient Record'
    };

    if (frm.doc.__islocal) {
      hide_field(['address_html']);
      frappe.contacts.clear_address_and_contact(frm);
    } else {
      unhide_field(['address_html']);
      frappe.contacts.render_address_and_contact(frm);
      erpnext.utils.set_party_dashboard_indicators(frm);
    }
    maia.patient_record.make_dashboard(frm);
  },

  invite_as_user: function(frm) {
    frm.save();
    var d = new frappe.ui.Dialog({
      'title': __('Create a New Website User ?'),
      fields: [{
          fieldtype: "HTML",
          options: __("Are you certain you want to create a website user for this patient ?")
        },
        {
          fieldname: 'ok_button',
          fieldtype: 'Button',
          label: __("Yes")
        },
      ]
    });
    d.show();
    d.fields_dict.ok_button.input.onclick = function() {
      d.hide();
      return frappe.call({
        method: "maia.maia.doctype.patient_record.patient_record.invite_user",
        args: {
          patient: frm.doc.name
        },
        callback: function(r) {
          if (r.message){
              frm.set_value("website_user", r.message);
              frm.save();
          } else {
            frappe.msgprint(__("Something went wrong during the user creation.<br>Please check with the support team."))
          }

        }
      });
    };
  },
  mobile_no: function(frm) {
    var reg = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/
    if (!frm.doc.mobile_no.match(reg)) {
      frappe.msgprint(__("The mobile n° format is incorrect"));
    }
  },
  weight: function(frm) {
    if (frm.doc.weight) {
      frm.save();
      frappe.call({
        method: "maia.maia.doctype.patient_record.patient_record.update_weight_tracking",
        args: {
          doc: frm.doc.name,
          weight: frm.doc.weight
        },
        callback: function(r) {
          if (r.message == 'Success') {
            frappe.show_alert({
              message: __("Weight Updated"),
              indicator: 'green'
            });
            frm.trigger("setup_chart");
          }
        }
      })
    }
  },
  setup_chart: function(frm) {

    frappe.call({
      method: "maia.maia.doctype.patient_record.patient_record.get_patient_weight_data",
      args: {
        patient_record: frm.doc.name
      },
      callback: function(r) {
        if (r.message && r.message[0].datasets[0].values.length !=0) {
          let data = r.message[0];
          let formatted_x = r.message[1];

          let $wrap = $('div[data-fieldname=weight_curve]').get(0);

          let chart = new Chart({
            parent: $wrap,
            title: __("Patient Weight"),
            data: data,
            type: 'line',
            region_fill: 1,
            height: 150,
            format_tooltip_y: d => d + ' Kg',
            colors: ['#ffa00a'],
          });
        }
      }
    });
  }

});

frappe.ui.form.on("Patient Record", "patient_date_of_birth", function(frm) {

  today = new Date();
  birthDate = new Date(frm.doc.patient_date_of_birth);
  if (today < birthDate) {
    frappe.msgprint(__('Please select a valid Date'));
    frappe.model.set_value(frm.doctype, frm.docname, "patient_date_of_birth", null)
  } else {
    age_yr = today.getFullYear() - birthDate.getFullYear();
    today_m = today.getMonth() + 1 //Month jan = 0
    birth_m = birthDate.getMonth() + 1 //Month jan = 0
    m = today_m - birth_m;

    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age_yr--;
    }

    age_str = null
    if (age_yr > 0)
      age_str = age_yr + " " + __('Years Old')

    frappe.model.set_value(frm.doctype, frm.docname, "patient_age", age_str)
  }
});

frappe.ui.form.on("Patient Record", "spouse_date_of_birth", function(frm) {

  today = new Date();
  birthDate = new Date(frm.doc.spouse_date_of_birth);
  if (today < birthDate) {
    frappe.msgprint(__('Please select a valid Date'));
    frappe.model.set_value(frm.doctype, frm.docname, "spouse_date_of_birth", null)
  } else {
    age_yr = today.getFullYear() - birthDate.getFullYear();
    today_m = today.getMonth() + 1 //Month jan = 0
    birth_m = birthDate.getMonth() + 1 //Month jan = 0
    m = today_m - birth_m;

    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age_yr--;
    }

    age_str = null
    if (age_yr > 0)
      age_str = age_yr + " " + __('Years Old')

    frappe.model.set_value(frm.doctype, frm.docname, "spouse_age", age_str)
  }
});

frappe.ui.form.on("Patient Record", "height", function(frm) {

  var weight = frm.doc.weight;
  var height = frm.doc.height;
  bmi = Math.round(weight / Math.pow(height, 2));
  frappe.model.set_value(frm.doctype, frm.docname, "body_mass_index", bmi)

});

frappe.ui.form.on("Patient Record", "weight", function(frm) {

  var weight = frm.doc.weight;
  var height = frm.doc.height;
  bmi = Math.round(weight / Math.pow(height, 2));
  frappe.model.set_value(frm.doctype, frm.docname, "body_mass_index", bmi)

});

frappe.ui.form.on("Patient Record", "pregnancies_report", function(frm) {
  return frappe.set_route('pregnancies', frm.doc.name);
});


$.extend(maia.patient_record, {
  make_dashboard: function(frm) {
    frappe.require('assets/js/patient-dashboard.min.js', function() {
  				var section = frm.dashboard.add_section('<div class="row"><button class="btn btn-xs btn-default btn-custom_dashboard">'+__("Memo")+'</button></div>');
  				maia.patient_record.custom_patient_dashboard = new maia.patient.PatientDashboard({
  					parent: section,
  					patient_record: frm.doc.name
  				});
  				maia.patient_record.custom_patient_dashboard.refresh();
  			});
    }
})
