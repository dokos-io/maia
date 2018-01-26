frappe.provide('maia.patient');

maia.patient.PatientDashboard = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.make();
	},
  make: function() {
    var me = this;
    this.content = $(frappe.render_template('custom_patient_dashboard')).appendTo(this.parent);
    this.result = this.content.find('.result');

    this.parent.on('click', '.btn-custom_dashboard', function() {
			me.show_options_dialog();
		});
  },
  refresh: function() {
		var me = this;
		frappe.call({
			method: 'maia.maia.doctype.patient_record.dashboard.custom_patient_dashboard.get_data',
			args: {
				patient_record: this.patient_record,
			},
			callback: function(r) {
        if (r.message) {
          me.render(r.message);
        }
			}
		});
	},
  render: function(data) {
    var context = data;
    $(frappe.render_template('custom_patient_dashboards', context)).appendTo(this.result);
  },
  show_options_dialog: function() {
    var me = this;
    let promises = [];
		let options_fields = {};

    function make_fields_from_options_values(options_fields) {
			let fields = [];
				options_fields.forEach(value => {
          if (fields.length === 3) {
            fields.push({fieldtype: 'Column Break'});
          }
					fields.push({
						fieldtype: 'Check',
						label: value.label,
						fieldname: value.name,
						default: value.value,
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
			return fields;
		}

    function make_and_show_dialog(fields) {
			me.options_dialog = new frappe.ui.Dialog({
				title: __("Select your dashboard options"),
				fields: [].concat(fields)
			});

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
            }
					}
				});
			});

			$($(me.options_dialog.$wrapper.find('.form-column'))
				.find('.frappe-control')).css('margin-bottom', '0px');

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
})
