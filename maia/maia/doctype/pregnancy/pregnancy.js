// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on('Pregnancy', {
	onload: function(frm) {
		frm.trigger("trigger_chart");
	},
	refresh: function(frm) {
		frm.trigger("trigger_chart");
		frm.add_custom_button(__('Calculate Term'), function() {
			get_term_date(frm);
		});
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

					let chart = new frappeChart.Chart($wrap, {
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
	},
	lab_exam_template: function(frm) {
		if(frm.doc.lab_exam_template) {
			frappe.call({
				"method": "maia.maia.doctype.lab_exam_template.lab_exam_template.get_lab_exam_template",
				args: {
					lab_exam_template: frm.doc.lab_exam_template
				},
				callback: function (data) {
					frappe.prompt([
						{'fieldname': 'date', 'fieldtype': 'Date', 'reqd': 1}
					],
					function(value){
						$.each(data.message || [], function(i, v){
							var d = frappe.model.add_child(frm.doc, "Lab Exam Results", "labs_results");
							d.date = value.date;
							d.exam_type = v.exam_type;
							frappe.db.get_value('Lab Exam Type', {name: d.exam_type}, 'default_value', (r) => {
									d.show_on_dashboard = r.default_value;
							});
						});
						refresh_field("labs_results");
					},
					__('Exams date ?'),
					__('Validate')
				);
				}
			});
		}
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

var get_term_date = function(frm) {
	let expected_term = frm.doc.expected_term;
	let beginning_of_pregnancy = frm.doc.beginning_of_pregnancy;
	let last_menstrual_period = frm.doc.last_menstrual_period;
	let current_date = frappe.datetime.nowdate();

	if (beginning_of_pregnancy != null) {
		am_weeks = Math.floor(frappe.datetime.get_diff(current_date, beginning_of_pregnancy) / 7) + 2
		add_days = Math.floor((frappe.datetime.get_diff(current_date, beginning_of_pregnancy) / 7 - Math.floor(frappe.datetime.get_diff(current_date, beginning_of_pregnancy) / 7)) * 7)
		frappe.show_alert({message: __("Calculated Term: {0} Weeks Amenorrhea + {1} Days", [am_weeks, add_days]), indicator: 'green'});

	} else if (expected_term != null) {
		am_weeks = Math.floor((287 - frappe.datetime.get_diff(expected_term, current_date)) / 7)
		add_days = Math.floor(((287 - frappe.datetime.get_diff(expected_term, current_date)) / 7 - am_weeks) * 7)
		frappe.show_alert({message: __("Calculated Term: {0} Weeks Amenorrhea + {1} Days", [am_weeks, add_days]), indicator: 'green'});

	} else if (last_menstrual_period != null) {
		am_weeks = Math.floor(frappe.datetime.get_diff(current_date, last_menstrual_period) / 7)
		add_days = Math.floor((frappe.datetime.get_diff(current_date, last_menstrual_period) / 7 - Math.floor(frappe.datetime.get_diff(current_date, last_menstrual_period) / 7)) * 7)
		frappe.show_alert({message: __("Calculated Term: {0} Weeks Amenorrhea + {1} Days", [am_weeks, add_days]), indicator: 'green'});

	} else {
		frappe.show_alert({message: __("Please set one of the following values: Beginning of pregnancy, expected term or last menstrual period"), indicator: 'orange'});
	}
};


{% include "maia/public/js/controllers/print_settings.js" %}
