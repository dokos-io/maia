# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		{
			"module_name": "Maia",
			"category": "Modules",
			"label": _("Medical Records"),
			"color": "#ff4081",
			"icon": "fas fa-stethoscope",
			"type": "module",
			"description": _("Your patient's medical records")
		},
		{
			"module_name": "Maia Accounting",
			"category": "Modules",
			"label": _("Accounting"),
			"color": "#3498db",
			"icon": "fas fa-book",
			"type": "module",
			"description": _("Revenue, expense, payments and reporting")
		},
		{
			"module_name": "Maia Appointment",
			"category": "Modules",
			"label": _("Appointments"),
			"color": "#8e44ad",
			"icon": "fas fa-calendar-alt",
			"type": "module",
			"description": _("Your appointments and calendar")
		}

	]