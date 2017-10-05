// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Midwife Appointment', {
  onload: function(frm) {
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
        if (!data.exe && data.message && data.message.name != null) {
          frappe.model.set_value(frm.doctype, frm.docname, "practitioner", data.message.name)
        }
      }
    });

    frm.set_df_property('appointment_type', 'reqd', 1);
    frm.set_df_property('patient_record', 'reqd', 1);
    frm.set_query("appointment_type", function() {
      var practitioners = [frm.doc.practitioner, ""]
        return {
            "filters": {
                "practitioner": ["in", practitioners],
            }
        };
    });
  },
  onload_post_render: function(frm) {
    frappe.model.set_value(frm.doctype, frm.docname, 'date', moment(frm.doc.start_dt).format(moment.defaultDateFormat));
    frappe.model.set_value(frm.doctype, frm.docname, 'start_time', moment(frm.doc.start_dt).format('H:mm:ss'));
  },
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      frm.add_custom_button(__('Personal Event'), function() {
        set_personal_event(frm);
      });

      frm.add_custom_button(__('Check Availability'), function() {
        check_availability_by_midwife(frm);
      });
    }
  },
  practitioner: function(frm) {

  },
  appointment_type: function(frm) {
    duration_and_color(frm);
  },
  all_day: function(frm) {
    if (frm.doc.all_day == 1) {
      frm.set_df_property('start_time', 'hidden', 1);
      frm.set_df_property('duration', 'hidden', 1);
    } else {
      frm.set_df_property('start_time', 'hidden', 0);
      frm.set_df_property('duration', 'hidden', 0);
    }
  },
  sms_reminder: function(frm) {
    if (frm.doc.patient_record && frm.doc.sms_reminder == 1) {
      frappe.call({
        "method": "frappe.client.get",
        args: {
          doctype: "Patient Record",
          name: frm.doc.patient_record,
          fieldname: "mobile_no"
        },
        cache: false,
        callback: function(data) {
          if (!data.exe && data.message) {
            frappe.model.set_value(frm.doctype, frm.docname, "mobile_no", data.message.mobile_no);
          }
        }
      });
    } else if (frm.doc.sms_reminder == 0) {
      frappe.model.set_value(frm.doctype, frm.docname, "mobile_no", "");
    }
  },
  patient_record: function(frm) {
    if (frm.doc.patient_record && frm.doc.reminder == 1) {
      frappe.call({
        "method": "frappe.client.get",
        args: {
          doctype: "Patient Record",
          name: frm.doc.patient_record,
          fields: ["email_id", "mobile_no"]
        },
        cache: false,
        callback: function(data) {
          if (data.message.email_id == null) {
            frappe.model.set_value(frm.doctype, frm.docname, "email", __("Enter an Email Address"));
            frm.set_df_property("email", "read_only", 0);
          } else if (!data.exe && data.message.email_id) {
            frappe.model.set_value(frm.doctype, frm.docname, "email", data.message.email_id);
            frm.set_df_property("email", "read_only", 1);
          }

          if (!data.exe && data.message.mobile_no && frm.doc.sms_reminder == 1) {
            frappe.model.set_value(frm.doctype, frm.docname, "mobile_no", data.message.mobile_no);
          }
        }
      });
    } else if (frm.doc.reminder == 0) {
      frappe.model.set_value(frm.doctype, frm.docname, "email", "");
    }
    frappe.model.set_value(frm.doctype, frm.docname, 'subject', frm.doc.patient_name);
  },
  mobile_no: function(frm) {
    if (frm.doc.sms_reminder == 1) {
      var reg = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/
      if (!frm.doc.mobile_no.match(reg)) {
        frappe.msgprint(__("The mobile n° format is incorrect"));
      }
    }
  },
  repeat_on: function(frm) {
    if (frm.doc.repeat_on === "Every Day") {
      $.each(["monday", "tuesday", "wednesday", "thursday", "friday",
        "saturday", "sunday"
      ], function(i, v) {
        frm.set_value(v, 1);
      });
    }
  }
});


var duration_and_color = function(frm) {
  if (frm.doc.appointment_type) {
    frappe.call({
      "method": "frappe.client.get",
      args: {
        doctype: "Midwife Appointment Type",
        name: frm.doc.appointment_type
      },
      callback: function(data) {
        frappe.model.set_value(frm.doctype, frm.docname, 'duration', data.message.duration);
        frappe.model.set_value(frm.doctype, frm.docname, 'color', data.message.color);
        frappe.model.set_value(frm.doctype, frm.docname, 'sms_reminder', data.message.send_sms_reminder);
      }
    });
  }
}

var btn_update_status = function(frm, status) {
  var doc = frm.doc;
  frappe.call({
    method: "maia.maia.doctype.midwife_appointment.midwife_appointment.update_status",
    args: {
      appointmentId: doc.name,
      status: status
    },
    callback: function(data) {
      if (!data.exc) {
        cur_frm.reload_doc();
      }
    }
  });
}

var set_personal_event = function(frm) {
  var df = frappe.meta.get_docfield("Midwife Appointment", "patient_record", frm.doc.name);
  frm.clear_custom_buttons();

  if (df.hidden == 0) {
    var perso = 0;
    var pub = 1;
    set_properties(frm, perso, pub);


    frm.add_custom_button(__('Patient Appointment'), function() {
      set_personal_event(frm);
    });

    frm.add_custom_button(__('Check Availability'), function() {
      check_availability_by_midwife(frm);
    });
  } else {
    var perso = 1;
    var pub = 0;
    set_properties(frm, perso, pub);

    frm.add_custom_button(__('Personal Event'), function() {
      set_personal_event(frm);
    });

    frm.add_custom_button(__('Check Availability'), function() {
      check_availability_by_midwife(frm);
    });
  }
}

var set_properties = function(frm, perso, pub) {
  frm.set_df_property('subject', 'hidden', perso);
  frm.set_df_property('subject', 'reqd', pub)
  frappe.model.set_value(frm.doctype, frm.docname, 'subject', '');
  frm.set_df_property('patient_record', 'reqd', perso);
  frm.set_df_property('patient_record', 'hidden', pub);
  frappe.model.set_value(frm.doctype, frm.docname, 'patient_record', '');
  frappe.model.set_value(frm.doctype, frm.docname, 'patient_name', '');
  frm.set_df_property('patient_name', 'hidden', pub);
  frappe.model.set_value(frm.doctype, frm.docname, 'appointment_type', '');
  frm.set_df_property('appointment_type', 'reqd', perso);
  frm.set_df_property('appointment_type', 'hidden', pub);
  frm.set_df_property('repeat_this_event', 'hidden', perso);
  frappe.model.set_value(frm.doctype, frm.docname, 'reminder', perso);
  frm.set_df_property('reminder', 'hidden', pub);
  frappe.model.set_value(frm.doctype, frm.docname, 'sms_reminder', 0);
  frm.set_df_property('sms_reminder', 'hidden', pub);
  frm.set_df_property('reminder_the_day_before', 'hidden', pub);
  frappe.model.set_value(frm.doctype, frm.docname, 'duration', '');
  frm.set_df_property('duration', 'read_only', perso);
  frm.set_df_property('duration', 'reqd', pub);
  frm.set_df_property('color', 'hidden', perso);
  frm.set_df_property('all_day', 'hidden', perso)
}

var check_availability_by_midwife = function(frm) {
  if (frm.doc.practitioner && frm.doc.date && frm.doc.duration) {
    frappe.call({
      method: "maia.maia.doctype.midwife_appointment.midwife_appointment.check_availability_by_midwife",
      args: {
        practitioner: frm.doc.practitioner,
        date: frm.doc.date,
        duration: frm.doc.duration
      },
      callback: function(r) {
        console.log(r.message)
        show_availability(frm, r.message)
      }
    });
  } else {
    frappe.msgprint(__("Please select a Midwife, a Date, an Appointment Type or a Duration"));
  }
}

var show_availability = function(frm, result) {
  var d = new frappe.ui.Dialog({
    title: __("Midwife Availability"),
    fields: [{
      fieldtype: "HTML",
      fieldname: "availability"
    }]
  });
  var html_field = d.fields_dict.availability.$wrapper;
  html_field.empty();
  var list = ''
  $.each(result, function(i, v) {
    if (!v[0]) {
      $(repl('<div class="col-xs-12" style="padding-top:20px;">' + __("No Availability") + '</div></div>')).appendTo(html_field);
      return
    }
    if (v[0]["msg"]) {
      var message = $(repl('<div class="col-xs-12" style="padding-top:20px;">%(msg)s</div></div>', {
        msg: v[0]["msg"]
      })).appendTo(html_field);
      return
    }
    $(repl('<div class="col-xs-12 form-section-heading uppercase"><h6> %(practitioner)s</h6></div>', {
      practitioner: i
    })).appendTo(html_field);
    if (v[0][0]["start"]) {
      var date = frappe.datetime.str_to_obj(v[0][0]["start"]);
      var options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      };
      $(repl('<div class="col-xs-12 border-bottom" style="margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd;"><h6> %(date)s</h6></div>', {
        date: date.toLocaleDateString('fr-FR', options)
      })).appendTo(html_field);
    }
    $.each(result[i][0], function(x, y) {
      if (y["msg"]) {
        var message = $(repl('<div class="col-xs-12" style="padding-top:12px; text-align:center;">%(msg)s</div></div>', {
          msg: y["msg"]
        })).appendTo(html_field);
        return
      } else {
        var start_time = frappe.datetime.str_to_obj(v[0][x]["start"]);
        var end_time = frappe.datetime.str_to_obj(v[0][x]["end"]);
        var row = $(repl('<div class="col-xs-12 list-customers-table border-left border-right border-bottom" style="padding-top:12px; text-align:center;" ><div class="col-xs-3"> %(start)s </div><div class="col-xs-2">-</div><div class="col-xs-3"> %(end)s </div><div class="col-xs-4"><a data-start="%(start)s" data-end="%(end)s" data-practitioner="%(practitioner)s"  href="#"><button class="btn btn-default btn-xs">' + __("Book") + '</button></a></div></div>', {
          start: start_time.toLocaleTimeString('fr-FR'),
          end: end_time.toLocaleTimeString('fr-FR'),
          practitioner: i
        })).appendTo(html_field);
      }
      row.find("a").click(function() {
        frm.doc.start_time = $(this).attr("data-start");
        refresh_field("start_time");
        frappe.model.set_value(frm.doctype, frm.docname, 'start_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time));
        d.hide()
        return false;
      });
    })

  });
  d.show();
}
