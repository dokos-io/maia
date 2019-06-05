var get_business_hours = function() {
	let mapping = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
	let agenda = [];
	frappe.call({
		async: false,
		"method": "maia.client.get_practitioner",
		args: {
			doctype: "Professional Information Card",
			filters: {
				user: frappe.session.user
			},
			fieldname: ["name", "consulting_schedule"]
		},
		callback: function (data) {
			if (data.message&&data.message.consulting_schedule.length>0) {
				data.message.consulting_schedule.forEach(value => {
					agenda.push({dow: [mapping[value.day]], start: value.start_time, end: value.end_time})
				})
				return agenda;
			} else {
				return agenda = false;
			}
		}
	});
	
	return (agenda)
}

frappe.views.calendar["Maia Appointment"] = {
	field_map: {
		"start": "start_dt",
		"end": "end_dt",
		"id": "name",
		"title": "subject",
		"allDay": "allDay",
		"color": "color"
	},
	gantt: false,
	get_events_method: "maia.maia_appointment.doctype.maia_appointment.maia_appointment.get_events",
	filters: [
		{
			'fieldtype': 'Link',
			'fieldname': 'patient_record',
			'options': 'Patient Record',
			'label': __('Patient')
		},
		{
			'fieldtype': 'Link',
			'fieldname': 'appointment_type',
			'options': 'Maia Appointment Type',
			'label': __('Appointment Type')
		}
	],
	options: {
		businessHours: get_business_hours(),
		minTime: '06:00:00',
		maxTime: '22:00:00',
		scrollTime: '08:00:00'
	}
}