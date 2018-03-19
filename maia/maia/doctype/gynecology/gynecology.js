// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gynecology', {

	onload: function(frm) {
		get_first_menses_and_regular_cycles(frm);
	},

	refresh: function(frm) {
		get_first_menses_and_regular_cycles(frm);
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
