frappe.views.calendar["Midwife Appointment"] = {
    field_map: {
	"start": "start_dt",
	"end": "end_dt",
	"id": "name",
	"title": "patient_record",
	"allDay": "allDay"
    },
    gantt: false,
    get_events_method: "maia.maia.doctype.midwife_appointment.midwife_appointment.get_events",
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
	    'options': 'Midwife Appointment Type',
	    'label': __('Appointment Type')
	}
    ]
}
