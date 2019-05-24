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
				}
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Maia Appointment Type",
					"label": _("Appointment Type"),
					"description": _("Maia Appointment Type"),
				}
			]
		}

	]
