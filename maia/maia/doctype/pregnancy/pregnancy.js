// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on('Pregnancy', {
  onload: function(frm) {
    frm.trigger("trigger_chart");
  },
  refresh: function(frm) {
    frm.trigger("trigger_chart");
  },
  date_time: function(frm) {
    frm.set_value("birth_datetime", frm.doc.date_time);
  },
  trigger_chart: function(frm) {
    if(frm.doc.birth_weight||frm.doc.release_weight) {
      frm.events.setup_newborn_chart(frm, 'firstchild', 'weight_curve');
    }
    if((frm.doc.twins||frm.doc.triplets)&&(frm.doc.birth_weight_2||frm.doc.release_weight_2)) {
      frm.events.setup_newborn_chart(frm, 'secondchild', 'weight_curve_2');
    }
    if((frm.doc.triplets)&&(frm.doc.birth_weight_3||frm.doc.release_weight_3)) {
      frm.events.setup_newborn_chart(frm, 'thirdchild', 'weight_curve_3');
    }
  },
  setup_newborn_chart: function(frm, child, domelem) {

    frappe.call({
      method: "maia.maia.doctype.pregnancy.pregnancy.get_newborn_weight_data",
      args: {
        patient_record: frm.doc.patient_record,
        pregnancy: frm.doc.name,
        child: child
      },
      callback: function(r) {
        if (r.message && r.message[0].datasets[0].values.length !=0) {
          let data = r.message[0];
          let colors = r.message[1];

          let $wrap = $('div[data-fieldname='+domelem+']').get(0);

          let chart = new Chart({
            parent: $wrap,
            title: __("Weight Curve (g)"),
            data: data,
            type: 'line',
            height: 150,
            format_tooltip_y: d => d + ' g',

            colors: colors,
          });
        }
      }
    });
  }
});

frappe.ui.form.on('Lab Exam Results', {
  exam_type: function(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    frappe.db.get_value('Lab Exam Type', {name: row.exam_type}, 'default_value', (r) => {
        frappe.model.set_value(cdt, cdn, "show_on_dashboard", r.default_value);
    });
  }
});
