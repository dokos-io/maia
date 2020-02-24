// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.provide('maia.maia_appointment');

frappe.ui.form.on('Maia Appointment', {
	setup(frm) {
		frappe.realtime.on('event_synced', (data) => {
			frappe.show_alert({message: data.message, indicator: 'green'});
			frm.reload_doc();
		})
	},
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
	refresh: function(frm) {
		update_top_buttons(frm);
		if (frm.doc.group_event && (frm.doc.status !== "Cancelled")) {
			update_group_info(frm);
		}

		if (frm.doc.rrule) {
			new frappe.CalendarRecurrence(frm, false);
		}

		frappe.db.get_value("Google Settings", "Google Settings", "enable", r => {
			if (r&&r.enable==="1") {
				frm.toggle_display('sync_with_google_calendar', true);
			}
		})

		if (frm.doc.docstatus === 1) {
			frm.page.add_menu_item(__("Cancel"), function() {
				frappe.xcall("maia.maia_appointment.doctype.maia_appointment.maia_appointment.cancel_appointment", {doc: frm.doc.name})
				.then(r => frm.reload_doc())
			}, true);
		}
	},
	appointment_type: function(frm) {
		duration_color_group(frm);
	},
	patient_name: function(frm) {
		frm.set_value('subject', frm.doc.patient_name);
	},
	patient_record: function(frm) {
		frm.set_value('email', '');
		frm.set_value('mobile_no', '');
		if (frm.doc.patient_record) {
			frappe.db.get_value("Patient Record", frm.doc.patient_record, ["mobile_no", "email_id"], r => {
				r&&r.mobile_no&&frm.set_value('mobile_no', r.mobile_no);
				r&&r.email_id&&frm.set_value('email', r.email_id);
			})
		}
	},
	mobile_no: function(frm) {
		if (frm.doc.sms_reminder == 1&&frm.doc.mobile_no) {
			const reg = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/
			if (!frm.doc.mobile_no.match(reg)) {
				frappe.msgprint(__("The mobile n° format is incorrect"));
			}
		}
	},
	repeat_this_event: function(frm) {
		if(frm.doc.repeat_this_event === 1) {
			new frappe.CalendarRecurrence(frm, true);
		}
	},
	sync_with_google_calendar(frm) {
		frm.trigger('get_google_calendar');
	},
	get_google_calendar(frm) {
		if(frm.doc.practitioner) {
			frappe.db.get_value("Professional Information Card", frm.doc.practitioner, "google_calendar", r => {
				if (r) {
					r.google_calendar&&frm.set_value("google_calendar", r.google_calendar);
				}
			})
		}
	},
	practitioner(frm) {
		if (frm.doc.practitioner) {
			frappe.db.get_value("Professional Information Card", frm.doc.practitioner, "google_calendar_sync_by_default", r => {
				if (r) {
					r.google_calendar_sync_by_default&&frm.set_value("sync_with_google_calendar", r.google_calendar_sync_by_default);
				}
			})
		}
	},
	duration(frm) {
		if(frm.doc.start_dt && frm.doc.duration) {
			frm.trigger('set_end_dt')
		}
	},
	end_dt(frm) {
		if (frm.doc.start_dt && frm.doc.end_dt) {
			frm.trigger('set_duration')
		}
	},
	start_dt(frm) {
		if (frm.doc.start_dt && frm.doc.duration && !frm.doc.personal_event) {
			frm.trigger('set_end_dt')
		} else if (frm.doc.start_dt && frm.doc.end_dt) {
			frm.trigger('set_duration')
		}
	},
	set_duration(frm) {
		frm.set_value("duration", frappe.datetime.get_minute_diff(frappe.datetime.str_to_obj(frm.doc.end_dt), frappe.datetime.str_to_obj(frm.doc.start_dt)))
	},
	set_end_dt(frm) {
		frm.set_value("end_dt", frappe.datetime.add_minutes(frappe.datetime.str_to_obj(frm.doc.start_dt), frm.doc.duration))
	}

});

const update_top_buttons = frm => {
	if (frm.doc.status !== "Cancelled" && frm.doc.docstatus === 0) {
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
	}

	if (!frm.is_new() && !frm.doc.patient_record && !frm.doc.group_event) {
		frm.add_custom_button(__('New Patient Record'), function() {
			create_new_patient_record(frm);
		});
	}
}


const duration_color_group = frm => {
	const doc = frm.doc
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
					slot_choice_modal(frm, data.message);
				}
			}
		});
	}
}

const set_personal_event = frm => {
	frm.clear_custom_buttons();
	frappe.model.set_value(frm.doctype, frm.docname, 'group_event', 0);
	if (frm.doc.personal_event == 0 || frm.doc.personal_event == undefined) {
		frappe.model.set_value(frm.doctype, frm.docname, 'personal_event', 1);

		const perso = 0;
		const pub = 1;
		set_values(frm, perso);

		update_top_buttons(frm);
	} else {
		frappe.model.set_value(frm.doctype, frm.docname, 'personal_event', 0);

		const perso = 1;
		const pub = 0;
		set_values(frm, perso);

		update_top_buttons(frm);
	}
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
	if (frm.doc.practitioner && frm.doc.start_dt && frm.doc.duration) {
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
			date: (frm.doc.start_dt || frappe.datetime.get_today())
		}
	}).then(r => {
		if (r.message) {
			const event = r.message.filter(f => f.name == frm.doc.name)
			const group_event = event.length ? event[0] : {}
			if (!event.length) { return }

			frm.set_value("seats_left", group_event.seats_left);
			$(`[data-fieldname="seats_left"]`).addClass(group_event.seats_left > 0 ? 'green-response' : 'red-response');
			frm.refresh_field("seats_left");

			$(frm.fields_dict['group_event_info'].wrapper).html(frappe.render_template("group_event_info", {data: group_event}))
		}
	})
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
		patient_record: frm.doc.name,
		frm: frm
	});
}

const slot_choice_modal = function(frm, data) {
	new maia.maia_appointment.SlotChoiceModal({
		parent: frm.doc,
		patient_record: frm.doc.name,
		data: data,
		frm: frm
	});
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
		const me = this;

		function make_and_show_dialog(result) {
			const d = new frappe.ui.Dialog({
				title: __("Midwife Availability"),
				fields: [{
					fieldtype: 'HTML',
					fieldname: 'availability',
				}]
			});
			const $html_field = d.fields_dict.availability.$wrapper;
			$html_field.empty();
			$(d.body).find('.form-section').css('padding-bottom', '12px');

			if (!result[me.parent.practitioner].length) {
				$(`<div class="col-xs-12" style="padding: 20px 0;">${__("No Availability")}</div></div>`).appendTo($html_field);
			} else if (result[me.parent.practitioner].msg) {
				$(`<div class="col-xs-12" style="padding:20px 0;">${msg}</div></div>`).appendTo($html_field);
			} else {
				$(`<div class="col-xs-12 form-section-heading uppercase">
					<div class="col-xs-12 col-sm-7">
						<h5>${me.parent.practitioner}</h5>
					</div>
					<div class="col-xs-12 col-sm-5 comparison-view" style="padding-right: 15px; padding-top: 3px">
					</div>
				</div>`).appendTo($html_field);

				const date = frappe.datetime.str_to_obj(result[me.parent.practitioner][0].start);
				const options = {
					weekday: 'long',
					year: 'numeric',
					month: 'long',
					day: 'numeric'
				};
				$(`<div class="col-xs-12 border-bottom" style="margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd;"><h6> ${date.toLocaleDateString('fr-FR', options)}</h6></div>`).appendTo($html_field);

				add_practitioners_selector();
			}

			result[me.parent.practitioner].forEach(value => {
				const start_time = frappe.datetime.str_to_obj(value.start);
				const end_time = frappe.datetime.str_to_obj(value.end);
				const row = $(`<div class="col-xs-12 list-customers-table border-left border-right border-bottom" style="padding-top: 6px; padding-bottom: 6px; text-align:center;" >
							<div class="col-xs-3">${start_time.toLocaleTimeString('fr-FR')}</div>
							<div class="col-xs-2">-</div>
							<div class="col-xs-3">${end_time.toLocaleTimeString('fr-FR')}</div>
							<div class="col-xs-4">
								<a class="booking" data-start="${start_time.toLocaleTimeString('fr-FR')}" data-end="${end_time.toLocaleTimeString('fr-FR')}" data-practitioner="${me.parent.practitioner}" href="#">
									<button class="btn btn-default btn-xs">${__("Book")}</button>
								</a>
							</div>
						</div>`).appendTo($html_field);

				row.find(".booking").click(function() {
					me.frm.set_value('start_dt', frappe.datetime.get_datetime_as_string(start_time));
					me.frm.refresh_fields("start_dt");
					me.frm.refresh_fields("end_dt");
					d.hide()
					return false;
				});
			})

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

		frappe.xcall('maia.maia_appointment.doctype.maia_appointment.maia_appointment.check_availability_by_midwife',
			{ practitioner: me.parent.practitioner, date: (me.parent.start_dt || frappe.datetime.get_today()), duration: me.parent.duration, appointment_type: me.parent.appointment_type },
		).then(r => {
			if (r&&r == "group_appointment") {
				duration_color_group(me.frm);
			} else if (r) {
				make_and_show_dialog(r);
			}
		});
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

		function make_and_show_dialog(fields, result) {
			me.options_dialog = new frappe.ui.Dialog({
				title: me.data.appointment_type,
				fields: [].concat(fields)
			});

			$($(me.options_dialog.$wrapper.find('.form-column')).find('.frappe-control')).css('margin-bottom', '0px');

			result.forEach(value => {
				const date = frappe.datetime.str_to_obj(value.start_dt);
				const options = {
					weekday: 'long',
					year: 'numeric',
					month: 'long',
					day: 'numeric'
				};
				const start_time = frappe.datetime.str_to_obj(value.start_dt);
				const end_time = frappe.datetime.str_to_obj(value.end_dt);
				const seats_left = value.already_registered ? (me.data.number_of_patients - value.already_registered) : me.data.number_of_patients
	
				if (seats_left > 0) {
					$(`<div class="col-xs-12 border-bottom" style="margin-top: 20px; margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd; border-radius: 4px 4px 0px 0px; text-align:center;">
							<h2>${me.parent.practitioner}</h2>
							<h6>${date.toLocaleDateString('fr-FR', options)}</h6>
							<h6> ${start_time.toLocaleTimeString('fr-FR')} - ${end_time.toLocaleTimeString('fr-FR')}</h6>
							<h6 style="color: green"> ${seats_left} ${__("seats left") }</h6>
						</div>`
					).appendTo(me.options_dialog.fields_dict[value.name].$wrapper);

					const row = $(`<div class="col-xs-12 list-customers-table border-left border-right border-bottom" style="padding-top:12px; padding-bottom:12px; text-align:center; border-radius: 0px 0px 4px 4px;">
						<div class="col-xs-4 col-xs-offset-4">
							<a data-start="${value.start_dt}" data-practitioner="${value.practitioner}" href="#" class="booking">
								<button class="btn btn-default btn-xs">${__("Book")}</button>
							</a>
						</div>
						</div>`
					).appendTo(me.options_dialog.fields_dict[value.name].$wrapper);

					row.find(".booking").click(function() {
						me.frm.set_value('practitioner', value.practitioner);
						me.frm.set_value('start_dt', frappe.datetime.get_datetime_as_string(value.start_dt));
						me.frm.refresh_fields("practitioner");
						me.frm.refresh_fields("start_dt");
						me.frm.refresh_fields("end_dt");
						me.options_dialog.hide()
						return false;
					});
				} else {
					$(`<div class="col-xs-12 border-bottom" style="margin-top: 20px; margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd; border-radius: 4px; text-align:center;">
							<h2>%(practitioner)s</h2>
							<h6>${date.toLocaleDateString('fr-FR', options)}</h6>
							<h6> ${start_time.toLocaleTimeString('fr-FR')} - ${end_time.toLocaleTimeString('fr-FR')}</h6>
							<h6 style="color: red"> ${seats_left} ${__("seats left")}</h6>
						</div>`
					).appendTo(me.options_dialog.fields_dict[value.name].$wrapper);
				}
			});

			me.options_dialog.clear();
			me.options_dialog.show();
		}

		frappe.xcall('maia.maia_appointment.doctype.maia_appointment.maia_appointment.get_registration_count',
			{ date: (me.parent.start_dt || frappe.datetime.get_today()), appointment_type: me.data.name }
		).then(r => {
			if (r&&r.length) {
				const fields = make_fields_from_options_values(r)
				make_and_show_dialog(fields, r);
			} else {
				frappe.msgprint(__('Please create at least one slot for this appointment type'))
			}
		});
	}
}
