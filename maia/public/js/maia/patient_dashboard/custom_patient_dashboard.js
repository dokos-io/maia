import Vue from 'vue/dist/vue.js';
import DashboardBase from './DashboardBase.vue';

Vue.prototype.__ = window.__;
frappe.provide('maia.patient');
frappe.provide('maia.updates');

maia.patient.PatientDashboard = class PatientDashboard{
	constructor(opts) {
		$.extend(this, opts);
		this.make();
	}

	make() {
		const me = this;
		this.parent.on('click', '.btn-custom_dashboard', function() {
			me.show_options_dialog();
		});
	}

	refresh() {
		this.render();
	}

	render() {
		new Vue({
			el: $(this.parent).find('#patient-dashboard-section')[0],
			render: h => h(DashboardBase),
			data: {
				'patient_record': this.patient_record
			}
		});
	}

	show_options_dialog() {
		var me = this;
		let promises = [];
		let options_fields = {};

		function make_fields_from_options_values(options_fields) {
			let fields = [];
				options_fields.forEach((value, index) => {
					if ((index > (Object.keys(options_fields).length / 2)) && (index < (Object.keys(options_fields).length / 2 + 1)))  {
            fields.push({fieldtype: 'Column Break'});
          }

					fields.push({
						fieldtype: 'Heading',
						label: Object.keys(value),
						fieldname: Object.keys(value),
					});
					Object.keys(value).forEach(d => {
						var fieldsToBeAdded = value[d];
						Object.keys(fieldsToBeAdded).forEach(e => {
							fields.push({
								fieldtype: 'Check',
								label: fieldsToBeAdded[e].label,
								fieldname: fieldsToBeAdded[e].name,
								default: fieldsToBeAdded[e].value,
								onchange: function() {
									let selected_options = get_selected_options();
									let lengths = [];
									Object.keys(selected_options).map(key => {
										lengths.push(selected_options[key].length);
									});
										me.options_dialog.get_primary_btn();
										me.options_dialog.enable_primary_action();
								}
							});
						});
					});
				});
			return fields;
		}

		function make_and_show_dialog(fields) {
			me.options_dialog = new frappe.ui.Dialog({
				title: __("Select your dashboard options"),
				fields: [].concat(fields)
			});

			function get_select_buttons() {
				return $(`<div style="margin-top: 15px;"><button class="btn btn-xs btn-default select-all">
					${__("Select All")}</button>
					<button class="btn btn-xs btn-default deselect-all">
				${__("Unselect All")}</button></div>`);
			}

			me.$select_buttons = get_select_buttons().appendTo(me.options_dialog.body);

			me.options_dialog.set_primary_action(__("Save"), () => {
				let selected_options = get_selected_options();

				me.options_dialog.hide();
				frappe.call({
					method:"maia.maia.doctype.patient_record.dashboard.custom_patient_dashboard.update_dashboard",
					args: {
						"patient_record": me.patient_record,
						"options": selected_options
					},
					callback: function(r) {
						if (r.message == "Success") {
							frappe.show_alert({
								message: __("This Patient's Memo has been updated"),
								indicator: 'green'
							});
							maia.updates.trigger('refresh_dashboard');
						}
					}
				});
			});

			$($(me.options_dialog.$wrapper.find('.form-column'))
				.find('.frappe-control')).css('margin-bottom', '0px');

			let select_all = (select=false) => {
				let $wrapper = me.options_dialog.$wrapper.find('.form-column');
				let checked_opts = $wrapper.find('.checkbox input');
				checked_opts.each((i, opt) => {
					$(opt).prop("checked", select);
				});
			}
			me.$select_buttons.find('.select-all').on('click', () => {
				select_all(true);
			});
			me.$select_buttons.find('.deselect-all').on('click', () => {
				select_all();
			});

			me.options_dialog.clear();
			me.options_dialog.show();
		}

		function get_selected_options() {
			let selected_options = [];
			let $wrapper = me.options_dialog.$wrapper.find('.form-column');
			let checked_opts = $wrapper.find('.checkbox input');
			checked_opts.each((i, opt) => {
				var fieldname = $(opt).attr('data-fieldname');
				var obj = {}
				if($(opt).is(':checked')) {
					obj[fieldname] = 1;
				} else {
					obj[fieldname] = 0;
				}
				selected_options.push(obj);
			});

			return selected_options;
		}

		let p = new Promise(resolve => {
			frappe.call({
					 method: 'maia.maia.doctype.patient_record.dashboard.custom_patient_dashboard.get_options',
					 args: {
						patient_record: this.patient_record,
					 },
			}).then((r) => {
				if (r.message) {
						options_fields = r.message;
						resolve();
				}
			});
		});
		promises.push(p);

		Promise.all(promises).then(() => {
			let fields = make_fields_from_options_values(options_fields);
			make_and_show_dialog(fields);
		})

	}
}

frappe.utils.make_event_emitter(maia.updates);