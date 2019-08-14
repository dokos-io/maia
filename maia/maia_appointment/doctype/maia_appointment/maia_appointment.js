// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia.maia_appointment');

frappe.ui.form.on('Maia Appointment', {
	onload: function(frm) {
		if (frm.doc.__islocal) {
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
		}

		if (frm.doc.personal_event === 0 || frm.doc.personal_event === undefined) {
			set_properties(frm, 1, 0);
			if (frm.doc.group_event == 1) {
				frm.set_df_property('patient_record', 'reqd', 0);
			}
		} else {
			set_properties(frm, 0, 1);
		}

		frm.set_query("appointment_type", function() {
			const practitioners = [frm.doc.practitioner, ""]
			return {
				"filters": {
					"practitioner": ["in", practitioners],
					"disabled": ["=", 0]
				}
			};
		});
		frm.add_web_link("/appointment", __('Online booking platform'))
	},
	onload_post_render: function(frm) {
		if (frm.doc.__islocal) {
			frm.set_value('date', moment(frm.doc.start_dt).format(moment.defaultDateFormat));
			frm.set_value('start_time', moment(frm.doc.start_dt).format('H:mm:ss'));
		}
	},
	refresh: function(frm) {
		update_top_buttons(frm);
		if (frm.doc.group_event && (frm.doc.docstatus === 1)) {
			update_group_info(frm);
		}
	},
	appointment_type: function(frm) {
		duration_color_group(frm.doc);
	},
	sms_reminder: function(frm) {
		if (frm.doc.patient_record && frm.doc.sms_reminder == 1) {
			patient_data(frm.doc.patient_record)
			.then(data => {
				if (data.message&&data.message.mobile_no) {
					frm.set_value("mobile_no", data.message.mobile_no);
				}
			})
		} else if (frm.doc.sms_reminder == 0) {
			frm.set_value("mobile_no", "");
		}
	},
	patient_record: function(frm) {
		if (frm.doc.patient_record && frm.doc.reminder == 1) {
			patient_data(frm.doc.patient_record)
			.then(data => {
				if (data.message.email_id == null) {
					frm.set_value("email", __("Enter an Email Address"));
					frm.set_df_property("email", "read_only", 0);
				}

				if (data.message.email_id == __("Enter an Email Address")) {
					frm.set_df_property("email", "read_only", 0);
				} else if (data.message.email_id) {
					frm.set_value("email", data.message.email_id);
					frm.set_df_property("email", "read_only", 1);
				}

				if (data.message.mobile_no && frm.doc.sms_reminder == 1) {
					frm.set_value("mobile_no", data.message.mobile_no);
				}
			})
		} else if (frm.doc.reminder == 0) {
			frm.set_value("email", "");
		}
	},
	patient_name: function(frm) {
		frm.set_value('subject', frm.doc.patient_name);
	},
	mobile_no: function(frm) {
		if (frm.doc.sms_reminder == 1&&frm.doc.mobile_no) {
			const reg = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/
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

const patient_data = patient_record => {
	return frappe.db.get_value("Patient Record", patient_record, ["mobile_no", "email_id"])
}

const update_top_buttons = frm => {
	if (frm.doc.docstatus == 0) {
		if (!frm.doc.personal_event) {
			if (!frm.doc.group_event) {
				frm.add_custom_button(__('Group Appointment'), function() {
					set_group_event(frm);
				});
			} else {
				frm.add_custom_button(__('Patient Appointment'), function() {
					set_group_event(frm);
				});
			}

			frm.add_custom_button(__('Personal Event'), function() {
				set_personal_event(frm);
			});
		} else {
			frm.add_custom_button(__('Patient Appointment'), function() {
				set_personal_event(frm);
			});
		}
		frm.add_custom_button(__('Check Availability'), function() {
			check_availability_by_midwife(frm);
		});
	} else if (frm.doc.docstatus == 1) {
		if (!frm.doc.patient_record && !frm.doc.group_event) {
			frm.add_custom_button(__('New Patient Record'), function() {
				create_new_patient_record(frm);
			});
		}
	}
}


const duration_color_group = doc => {
	if (doc.appointment_type) {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Maia Appointment Type",
				name: doc.appointment_type
			},
			callback: function(data) {
				frappe.model.set_value(doc.doctype, doc.name, 'duration', data.message.duration);
				frappe.model.set_value(doc.doctype, doc.name, 'color', data.message.color);
				frappe.model.set_value(doc.doctype, doc.name, 'sms_reminder', data.message.send_sms_reminder);

				if (data.message.group_appointment == 1 && doc.group_event == 1) {
					frappe.model.set_value(doc.doctype, doc.name, 'number_of_seats', data.message.number_of_patients);
					frappe.model.set_value(doc.doctype, doc.name, 'subject', data.message.appointment_type + "-" + __("Group"));
				} else if (data.message.group_appointment == 1 && !doc.group_event) {
					slot_choice_modal(doc, data.message);
				}
			}
		});
	}
}

const btn_update_status = (frm, status) => {
	frappe.call({
		method: "maia.maia_appointment.doctype.maia_appointment.maia_appointment.update_status",
		args: {
			appointmentId: frm.doc.name,
			status: status
		},
		callback: function(data) {
			if (!data.exc) {
				cur_frm.reload_doc();
			}
		}
	});
}

const set_personal_event = frm => {
	frm.clear_custom_buttons();
	frappe.model.set_value(frm.doctype, frm.docname, 'group_event', 0);
	if (frm.doc.personal_event == 0 || frm.doc.personal_event == undefined) {
		frappe.model.set_value(frm.doctype, frm.docname, 'personal_event', 1);

		const perso = 0;
		const pub = 1;
		set_properties(frm, perso, pub);
		set_values(frm, perso);

		update_top_buttons(frm);
	} else {
		frappe.model.set_value(frm.doctype, frm.docname, 'personal_event', 0);

		const perso = 1;
		const pub = 0;
		set_properties(frm, perso, pub);
		set_values(frm, perso);

		update_top_buttons(frm);
	}
}

const set_properties = (frm, perso, pub) => {
	frm.set_df_property('subject', 'reqd', pub)
	frm.set_df_property('patient_record', 'reqd', perso);
	frm.set_df_property('appointment_type', 'reqd', perso);
	frm.set_df_property('duration', 'read_only', perso);
	frm.set_df_property('duration', 'reqd', pub);
}

const set_values = (frm, perso) => {
	frappe.model.set_value(frm.doctype, frm.docname, 'subject', '');
	frappe.model.set_value(frm.doctype, frm.docname, 'patient_record', '');
	frappe.model.set_value(frm.doctype, frm.docname, 'patient_name', '');
	frappe.model.set_value(frm.doctype, frm.docname, 'appointment_type', '');
	frappe.model.set_value(frm.doctype, frm.docname, 'reminder', perso);
	frappe.model.set_value(frm.doctype, frm.docname, 'sms_reminder', 0);
	frappe.model.set_value(frm.doctype, frm.docname, 'duration', 0);
}

const set_group_event = frm => {
	frm.clear_custom_buttons();
	if (!frm.doc.group_event) {
		frappe.model.set_value(frm.doctype, frm.docname, 'group_event', 1);
		frm.set_df_property('patient_record', 'reqd', 0);
		frappe.model.set_value(frm.doctype, frm.docname, 'reminder', 0);
		frappe.model.set_value(frm.doctype, frm.docname, 'sms_reminder', 0);
		frm.set_query("appointment_type", function() {
			const practitioners = [frm.doc.practitioner, ""]
			return {
				"filters": {
					"practitioner": ["in", practitioners],
					"group_appointment": 1
				}
			};
		});
	} else {
		frappe.model.set_value(frm.doctype, frm.docname, 'group_event', 0);
		frm.set_df_property('patient_record', 'reqd', 1);
		frappe.model.set_value(frm.doctype, frm.docname, 'reminder', 1);
		frm.set_query("appointment_type", function() {
			const practitioners = [frm.doc.practitioner, ""]
			return {
				"filters": {
					"practitioner": ["in", practitioners]
				}
			};
		});
	}
	update_top_buttons(frm);
}

const check_availability_by_midwife = frm => {
	if (frm.doc.practitioner && frm.doc.date && frm.doc.duration) {
		show_availability(frm);
	} else {
		frappe.msgprint(__("Please select a Midwife, a Date, an Appointment Type or a Duration"));
	}
}

const update_group_info = frm => {
	frappe.call({
		method: "maia.maia_appointment.doctype.maia_appointment.maia_appointment.get_registration_count",
		args: {
			appointment_type: frm.doc.appointment_type,
			date: frm.doc.start_dt
		},
		callback: function(r, rt) {
			let eventData;
			if (r.message) {
				for (let i=0; i < r.message.length; i++) {
					if (r.message[i].name == frm.doc.name) {
						eventData = r.message[i]
					}
				}

				if (eventData) {
					frappe.call({
						method: "maia.maia_appointment.doctype.maia_appointment.maia_appointment.set_seats_left",
						args: {
							appointment: frm.doc.name,
							data: eventData
						},
						callback: function(r, rt) {
							if (r.message=='green'){
								$(`[data-fieldname="seats_left"]`).addClass('green-response');
							} else {
								$(`[data-fieldname="seats_left"]`).addClass('red-response');
							}
						}
					})

					$(frm.fields_dict['group_event_info'].wrapper).html(frappe.render_template("group_event_info", {data: eventData}))
				}

			}
		}
	});
}

const create_new_patient_record = function(frm) {
	frappe.model.with_doc("User", frm.doc.user, ()=> {
		let user = frappe.model.get_doc("User", frm.doc.user);
		const d = new frappe.ui.Dialog({
			title: __("Create a new patient record"),
			fields: [{
						"fieldtype": "Data",
						"label": __("First Name"),
						"fieldname": "first_name",
						"default": user.first_name
					},
					{
						"fieldtype": "Data",
						"label": __("Last Name"),
						"fieldname": "last_name",
						"default": user.last_name
					}
			]
		});
		d.set_primary_action(__("Create"), function() {
			const values = d.get_values();
			if (values) {
				d.hide();
				frappe.call({
					method: "maia.maia_appointment.doctype.maia_appointment.maia_appointment.create_patient_record",
					args: {
						data: values,
						user: frm.doc.user
					},
					callback: function(r, rt) {
						if (r.message == 'success') {
								frm.reload_doc();
								frappe.show_alert({
									message: __("Patient Record successfully created"),
									indicator: 'green'
								});
						} else {
							frappe.msgprint(__("An error occured during the creation. Please create your patient record manually."))
						}
					}
				})
		}
		});
		d.show();
	})
}

const show_availability = function(frm) {
	new maia.maia_appointment.AvailabilityModal({
		parent: frm.doc,
		patient_record: frm.doc.name
	});
}

const slot_choice_modal = function(doc, data) {
	if (doc.date) {
		new maia.maia_appointment.SlotChoiceModal({
			parent: doc,
			patient_record: doc.name,
			data: data
		});
	} else {
		frappe.msgprint(__('Please select a date'))
	}
}

maia.maia_appointment.AvailabilityModal = class AvailabilityModal {
	constructor(opts) {
		$.extend(this, opts);
		this.make();
	}

	make() {
		this.show_options_dialog();
	}

	additional_practitioners_dialog() {
		this.show_options_dialog();
	}

	show_options_dialog() {
		let me = this;
		let promises = [];
		function make_fields() {
			let fields = [];
			fields.push({
				fieldtype: 'HTML',
				fieldname: 'availability',
			});
			return fields;
		}

		function make_and_show_dialog(fields, result) {
			const d = new frappe.ui.Dialog({
				title: __("Midwife Availability"),
				fields: [].concat(fields)
			});
			const $html_field = d.fields_dict.availability.$wrapper;
			$html_field.empty();
			$(d.body).find('.form-section').css('padding-bottom', '12px');
			$.each(result, function(i, v) {
				if (!v[0]) {
					$(repl('<div class="col-xs-12" style="padding-top:20px;">' + __("No Availability") + '</div></div>')).appendTo($html_field);
					return
				}
				if (v[0]["msg"]) {
					$(repl('<div class="col-xs-12" style="padding-top:20px;">%(msg)s</div></div>', {
						msg: v[0]["msg"]
					})).appendTo($html_field);
					return
				}

				$(repl('<div class="col-xs-12 form-section-heading uppercase"><div class="col-xs-12 col-sm-7"><h5> %(practitioner)s</h5></div><div class="col-xs-12 col-sm-5 comparison-view" style="padding-right: 15px; padding-top: 3px"></div></div>', {
					practitioner: i
				})).appendTo($html_field);

				add_practitioners_selector();

				if (v[0][0]["start"]) {
					const date = frappe.datetime.str_to_obj(v[0][0]["start"]);
					const options = {
						weekday: 'long',
						year: 'numeric',
						month: 'long',
						day: 'numeric'
					};
					$(repl('<div class="col-xs-12 border-bottom" style="margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd;"><h6> %(date)s</h6></div>', {
						date: date.toLocaleDateString('fr-FR', options)
					})).appendTo($html_field);
				}

				$.each(result[i][0], function(x, y) {
					let row;
					if (y["msg"]) {
						row = $(repl('<div class="col-xs-12" style="padding-top:6px; padding-bottom: 6px; text-align:center;">%(msg)s</div></div>', {
							msg: y["msg"]
						})).appendTo($html_field);
						return
					} else {
						const start_time = frappe.datetime.str_to_obj(v[0][x]["start"]);
						const end_time = frappe.datetime.str_to_obj(v[0][x]["end"]);
						row = $(repl('<div class="col-xs-12 list-customers-table border-left border-right border-bottom" style="padding-top: 6px; padding-bottom: 6px; text-align:center;" ><div class="col-xs-3"> %(start)s </div><div class="col-xs-2">-</div><div class="col-xs-3"> %(end)s </div><div class="col-xs-4"><a class="booking" data-start="%(start)s" data-end="%(end)s" data-practitioner="%(practitioner)s"  href="#"><button class="btn btn-default btn-xs">' + __("Book") + '</button></a></div></div>', {
							start: start_time.toLocaleTimeString('fr-FR'),
							end: end_time.toLocaleTimeString('fr-FR'),
							practitioner: i
						})).appendTo($html_field);
					}

					row.find(".booking").click(function() {
						me.parent.start_time = $(this).attr("data-start");
						refresh_field("start_time");
						frappe.model.set_value(me.parent.doctype, me.parent.docname, 'start_dt', moment.utc(me.parent.date + ' ' + me.parent.start_time));
						d.hide()
						return false;
					});

				})
			});

			function add_practitioners_selector() {
				frappe.call({
					"method": "frappe.client.get_list",
					args: {
						doctype: "Professional Information Card",
						fieldname: "name"
					},
					cache: false,
					callback: function(data) {
						if (data.message && data.message.length>1) {
							let el = $(frappe.render_template('custom_button', {'data': data.message}))
							el.appendTo($html_field.find('.comparison-view'));
						}
					}
				});
				$html_field.on('click', '.other_practitioner', function() {
					me.parent.practitioner = $(this).attr('id');
					refresh_field("practitioner");
					me.additional_practitioners_dialog();
					d.hide();
				});
			}

			d.show();
		}

		let result;
		let p = new Promise(resolve => {
				frappe.xcall('maia.maia_appointment.doctype.maia_appointment.maia_appointment.check_availability_by_midwife',
					{ practitioner: me.parent.practitioner, date: me.parent.date, duration: me.parent.duration, appointment_type: me.parent.appointment_type },
				).then(r => {
					if (r&&r == "group_appointment") {
						duration_color_group(me.parent);
					} else if (r) {
						result = r;
						resolve();
					}
				});
			});
			promises.push(p);

			Promise.all(promises).then(() => {
				let fields = make_fields();
				make_and_show_dialog(fields, result);
			})
	}
}

maia.maia_appointment.SlotChoiceModal = class SlotChoiceModal{
	constructor(opts) {
		$.extend(this, opts);
		this.make();
	}

	make() {
		this.show_options_dialog();
	}

	show_options_dialog() {
		const me = this;
		let promises = [];
		let options_fields = {};

		function make_fields_from_options_values(options_fields) {
			let fields = [];
			options_fields.forEach((value, index) => {
				if ((index > (Object.keys(options_fields).length / 2)) && (index < (Object.keys(options_fields).length / 2 + 1))) {
					fields.push({
						fieldtype: 'Column Break'
					});
				}
				fields.push({
					fieldtype: 'HTML',
					fieldname: value.name,
				});
			});
			return fields;
		}

		function make_and_show_dialog(fields) {
			me.options_dialog = new frappe.ui.Dialog({
				title: me.data.appointment_type,
				fields: [].concat(fields)
			});

			$($(me.options_dialog.$wrapper.find('.form-column'))
				.find('.frappe-control')).css('margin-bottom', '0px');

			options_fields.forEach((value, index) => {
				const date = frappe.datetime.str_to_obj(value.start_dt);
				const options = {
					weekday: 'long',
					year: 'numeric',
					month: 'long',
					day: 'numeric'
				};
				const start_time = frappe.datetime.str_to_obj(value.start_dt);
				const end_time = frappe.datetime.str_to_obj(value.end_dt);
				let seats_left;
				if (value.already_registered) {
					seats_left = me.data.number_of_patients - value.already_registered
				} else {
					seats_left = me.data.number_of_patients
				}

				if (seats_left > 0) {
					$(repl('<div class="col-xs-12 border-bottom" style="margin-top: 20px; margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd; border-radius: 4px 4px 0px 0px; text-align:center;"><h2>%(practitioner)s</h2><h6>%(date)s</h6><h6> %(start)s - %(end)s</h6><h6 style="color: green"> %(seats)s ' + __("seats left") + '</h6></div>', {
						date: date.toLocaleDateString('fr-FR', options),
						start: start_time.toLocaleTimeString('fr-FR'),
						end: end_time.toLocaleTimeString('fr-FR'),
						seats: seats_left,
						practitioner: value.practitioner
					})).appendTo(me.options_dialog.fields_dict[value.name].$wrapper);

					$(repl('<div class="col-xs-12 list-customers-table border-left border-right border-bottom" style="padding-top:12px; padding-bottom:12px; text-align:center; border-radius: 0px 0px 4px 4px;" ><div class="col-xs-4 col-xs-offset-4"><a data-start="%(start)s" data-practitioner="%(practitioner)s"  href="#"><button class="btn btn-default btn-xs">' + __("Book") + '</button></a></div></div>', {
						start: value.start_dt,
						practitioner: value.practitioner
					})).appendTo(me.options_dialog.fields_dict[value.name].$wrapper);
				} else {
					$(repl('<div class="col-xs-12 border-bottom" style="margin-top: 20px; margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd; border-radius: 4px; text-align:center;"><h2>%(practitioner)s</h2><h6>%(date)s</h6><h6> %(start)s - %(end)s</h6><h6 style="color: red"> %(seats)s ' + __("seats left") + '</h6></div>', {
						date: date.toLocaleDateString('fr-FR', options),
						start: start_time.toLocaleTimeString('fr-FR'),
						end: end_time.toLocaleTimeString('fr-FR'),
						seats: seats_left,
						practitioner: value.practitioner
					})).appendTo(me.options_dialog.fields_dict[value.name].$wrapper);
				}
			});

			me.options_dialog.wrapper.find("a").click(function() {
				me.options_dialog.start_time = $(this).attr("data-start");
				me.options_dialog.practitioner = $(this).attr("data-practitioner");
				frappe.model.set_value(me.parent.doctype, me.parent.name, 'practitioner', me.options_dialog.practitioner);
				frappe.model.set_value(me.parent.doctype, me.parent.name, 'date', frappe.datetime.obj_to_str(me.options_dialog.start_time));
				frappe.model.set_value(me.parent.doctype, me.parent.name, 'start_time', moment.utc(frappe.datetime.get_datetime_as_string(me.options_dialog.start_time)).format("HH:mm:ss"));
				frappe.model.set_value(me.parent.doctype, me.parent.name, 'start_dt', moment.utc(frappe.datetime.get_datetime_as_string(me.options_dialog.start_time)).format("YYYY-MM-DD HH:mm:ss"));
				me.options_dialog.hide()
				return false;
			});

			me.options_dialog.clear();
			me.options_dialog.show();
		}

		let p = new Promise(resolve => {
			frappe.xcall('maia.maia_appointment.doctype.maia_appointment.maia_appointment.get_registration_count',
				{ date: me.parent.date, appointment_type: me.data.name }
			).then(r => {
				if (r&&r.length) {
					options_fields = r;
					resolve();
				} else {
					frappe.msgprint(__('Please create at least one slot for this appointment type'))
				}
			});
		});
		promises.push(p);

		Promise.all(promises).then(() => {
			let fields = make_fields_from_options_values(options_fields);
			make_and_show_dialog(fields, options_fields);
		})
	}
}
