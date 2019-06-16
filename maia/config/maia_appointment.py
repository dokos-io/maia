from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Appointments"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Maia Appointment",
					"label": _("Appointment"),
					"description": _("Appointment"),
					"route": "#List/Maia Appointment",
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "SMS Reminder",
					"label": _("SMS Reminder"),
					"description": _("SMS Reminder")
				}
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Professional Information Card",
					"label": _("Professional Information Card"),
					"description": _("Professional Information Card"),
				},
				{
					"type": "doctype",
					"name": "Maia Appointment Type",
					"label": _("Appointment Type"),
					"description": _("Maia Appointment Type"),
				},
				{
					"type": "doctype",
					"name": "Maia Appointment Type Category",
					"label": _("Appointment Type Category"),
					"description": _("Appointment Type Category"),
				}
			]
		}

	]
