// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gynecology', {

	onload: function(frm) {
		get_first_menses_and_regular_cycles(frm);
	},

	refresh: function(frm) {
		get_first_menses_and_regular_cycles(frm);
		render_cervical_smears(frm);
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
	},



});

var render_cervical_smears = function(frm) {
	if(frm.fields_dict['cervical_smear_display']) {
		frappe.call({
			"method": "maia.maia.doctype.gynecology.gynecology.get_last_cervical_smears",
			args: {
				patient_record: frm.doc.patient_record
			},
			cache: false,
			callback: function(data) {
					$(frm.fields_dict['cervical_smear_display'].wrapper)
						.html(frappe.render_template("cervical_smears_template", {data: data.message}))
						.find(".btn-cervical-smears").on("click", function() {
							add_new_cervical_smear(frm);
						});
			}
		})

	}
};

var add_new_cervical_smear = function(frm) {
	var d = new frappe.ui.Dialog({
		'title': __("New Cervical Smear"),
		'fields': [
		{'fieldname': 'date', 'fieldtype': 'Data', 'label': __("Date"), 'reqd': 1},
		{'fieldname': 'result', 'fieldtype': 'Small Text', 'label': __("Result"), 'reqd': 1}
	],
	primary_action: function(){
		d.hide();
		const data = d.get_values()
		frappe.call({
			"method": "maia.maia.doctype.gynecology.gynecology.add_cervical_smear",
			args: {
				patient_record: frm.doc.patient_record,
				date: data.date,
				result: data.result
			},
			cache: false,
			callback: function(data) {
				if (data.message == 'Success') {
					frappe.show_alert(__('New cervical smear successfully added'));
					render_cervical_smears(frm);
				}
			}
		});
	}
});
d.show();
}

var get_first_menses_and_regular_cycles = function(frm) {
	if (frm.doc.patient_record) {
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Patient Record",
				name: frm.doc.patient_record
			},
			cache: false,
			callback: function(data) {
				if (data.message) {
					first_menses = data.message.first_menses;
					regular_cycles = data.message.regular_cycles;
					contraception = data.message.contraception;


					frappe.model.set_value(frm.doctype, frm.docname, "first_menses", first_menses);
					frappe.model.set_value(frm.doctype, frm.docname, "regular_cycles", regular_cycles);
					frappe.model.set_value(frm.doctype, frm.docname, "contraception", contraception);

				}
			}
		})
	}
};
