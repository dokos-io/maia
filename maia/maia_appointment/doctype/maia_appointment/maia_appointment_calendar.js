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
    ]
}
