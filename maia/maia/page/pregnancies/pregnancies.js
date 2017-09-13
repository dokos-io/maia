frappe.Pregnancies = Class.extend({

	init: function(parent) {
		var me = this;
		this.page = frappe.ui.make_app_page({
			parent: parent,
			title: __("Pregnancies"),
			single_column: true
		});

		me.patient_record = [];
		me.get_patients();
		me.filters = [];
		console.log(me)
		// for saving current selected filters
		const _selected_filter = me.filters[me.patient_record[0]];
		me.options = {
			selected_patient_record: me.patient_record[0],
		};

		this.message = null;
		this.make();
	},



	make: function() {

		var me = this;

		var $pregnancies = $(frappe.render_template("pregnancies", this)).appendTo(this.page.main);

		// events
		$pregnancies.find(".select-patient-record")
			.on("change", function() {
				me.options.selected_patient_record = this.value;
				me.make_request($pregnancies);
			});

		// now get pregnancies
		me.make_request($pregnancies);
	},

	make_request: function($pregnancies) {
		var me = this;
		me.get_pregnancies($pregnancies);
	},

	get_pregnancies: function($pregnancies) {
		var me = this;
		if (me.options.selected_patient_record != undefined) {
		frappe.call({
			method: "maia.maia.page.pregnancies.pregnancies.get_pregnancies",
			args: {
				obj: JSON.stringify(me.options)
			},
			callback: function(res) {
				console.log(res.message);
				if (!res.message) return;

					for (var i = 0; i < res.message.length; i++) {
						var pregnancy_data = res.message[i];
						if (pregnancy_data.data_type == "past_pregnancy") {
							$(frappe.render_template("past_pregnancies_result", pregnancy_data)).appendTo($pregnancies.find(".pregnancies"));
						} else {
							$(frappe.render_template("current_pregnancies_result", pregnancy_data)).appendTo($pregnancies.find(".pregnancies"));

					}
				}
			}
		});
	}
	},
	get_patients: function() {
		var me = this;
		console.log(me)
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Patient Record",
				order_by: "name"
			},
			callback: function(res) {
				var patients = [];
				for (var i = 0; i < res.message.length; i++) {
					patients.push(res.message[i].name);
				}
				console.log(patients)
				return me.patient_record = patients;
			}
		});
	}

});

frappe.pages["pregnancies"].on_page_load = function(wrapper) {
	frappe.pregnancies = new frappe.Pregnancies(wrapper);
}
