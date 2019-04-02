# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		{
			"module_name": "Calendar",
			"doctype": "Event",
			"color": "#ff4081",
			"icon": "octicon octicon-calendar",
			"type": "link",
			"link": "List/Maia Appointment/Calendar",
			"label": _("Calendar")
		},
		{
			"module_name": "Patient Record",
			"_doctype": "Patient Record",
			"color": "#ff4081",
			"icon": "fa fa-stethoscope",
			"type": "link",
			"link": "List/Patient Record",
			"label": _("Patients")
		},
		{
			"module_name": "Maia",
			"color": "#ff4081",
			"icon": "octicon octicon-squirrel",
			"type": "module",
			"label": _("Maia")
		}

	]