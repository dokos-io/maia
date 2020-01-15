import frappe
from frappe.desk.calendar import get_rrule

def execute():
	frappe.db.set_value("System Settings", "System Settings", "time_format", "HH:mm")

	frappe.reload_doc("maia", "maia_appointment", "maia_appointment")
	appointments = frappe.get_all("Maia Appointment", fields=["name", "docstatus", "repeat_this_event", "personal_event"])

	for appointment in appointments:
		if appointment.get("docstatus") == 1:
			frappe.db.set_value("Maia Appointment", booking.get("name"), "status", "Confirmed")
		elif appointment.get("docstatus") == 2:
			frappe.db.set_value("Maia Appointment", booking.get("name"), "status", "Cancelled")

		if appointment.personal_event and appointment.repeat_this_event:
			doc = frappe.get_doc("Maia Appointment", appointment.name)
			rrule = get_rrule(doc)
			if rrule:
				frappe.db.set_value("Maia Appointment", appointment.name, "rrule", rrule)

