# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
                {
                        "module_name": "Tools",
                        "doctype": "Event",
                        "color": "#ff4081",
			"icon": "octicon octicon-calendar",
			"type": "link",
                        "link": "Calendar/Event",
			"label": _("Calendar")
		},
                {
			"module_name": "Patient",
                        "_doctype": "Patient",
			"color": "#ff4081",
			"icon": "fa fa-stethoscope",
			"type": "link",
                        "link": "List/Patient",
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
