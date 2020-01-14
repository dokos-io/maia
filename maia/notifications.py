# Copyright (c) 2019, Dokos SAS and Contributors
# See license.txt

import frappe

def get_notification_config():
	return {
		"for_doctype": {
			"Pregnancy Consultation": {"docstatus": 0},
            "Birth Preparation Consultation": {"docstatus": 0},
            "Early Postnatal Consultation": {"docstatus": 0},
            "Postnatal Consultation": {"docstatus": 0},
            "Perineum Rehabilitation Consultation": {"docstatus": 0},
            "Gynecological Consultation": {"docstatus": 0},
            "Free Consultation": {"docstatus": 0},
            "Free Prescription": {"docstatus": 0},
            "Maia Appointment": {"name": ["in", get_todays_events()]},
            "Revenue": {"status": ["in", ["Unpaid", "Draft"]]},
            "Expense": {"status": ["in", ["Unpaid", "Draft"]]},
            "Miscellaneous Operation": {"docstatus": 0},
            "Payment": {"status": ["in", ["Draft", "Unreconciled"]]}
		}
	}

def get_todays_events():
	"""Returns a count of todays events in calendar"""
	from maia.maia_appointment.doctype.maia_appointment.maia_appointment import get_events
	from frappe.utils import nowdate
	today = nowdate()
	events = get_events(today, today, frappe.session.user)
	return [x.get("name") for x in events]