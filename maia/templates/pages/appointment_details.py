# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import formatdate, get_datetime_str, get_datetime, add_days, nowdate, getdate
import datetime

def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	appointment = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)
	context.doc = appointment
	if hasattr(context.doc, "set_indicator"):
		context.doc.set_indicator()

	context.parents = frappe.form_dict.parents
	context.title = frappe.form_dict.name

	cancellation_date = add_days(nowdate(), 2)
	if getdate(appointment.date) > getdate(cancellation_date):
		context.show_cancel_button = 1

#	if not frappe.has_website_permission(context.doc):
#		frappe.throw(_("Not Permitted"), frappe.PermissionError)

@frappe.whitelist()
def confirm_cancellation(context=None):
	return "Confirmed"

@frappe.whitelist()
def cancel_appointment(doc):
	appointment = frappe.get_doc("Midwife Appointment", doc)
	appointment.cancel()

	context =  {"doc": {"docstatus": appointment.docstatus, "end_dt": appointment.end_dt}}
	confirmation = frappe.render_template('templates/includes/appointments/cancellation_confirmation.html', context)
	status = frappe.render_template('templates/includes/appointments/appointment_status.html', context)

	send_cancellation_notification(appointment.patient_record, appointment.practitioner, appointment.appointment_type, appointment.start_dt, appointment.notes)

	return {"confirmation": confirmation, "status": status}

def send_cancellation_notification(patient_record, practitioner, appointment_type, start, notes):
			patient = frappe.get_doc("Patient Record", patient_record)
			if patient:
				patient_name = patient.name
			else:
				patient = frappe.get_doc("User", frappe.session.user)
				patient_name = patient.first_name + " " + patient.last_name

			practitioner_data = frappe.get_doc("Professional Information Card", practitioner)
			if practitioner_data.user:
				user_data = frappe.get_doc("User", practitioner_data.user)
				date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
				time = get_datetime(start).strftime("%H:%M")

				subject = _("""[Maia] Annulation d'un Rendez-Vous""")
				message = _("""<div>Bonjour {0},<br><br>{1} vient d'annuler le rendez-vous suivant:<br><br><strong>Date:</strong> {2}<br><br><strong>Heure:</strong> {3}<br><br><strong>Message:</strong> {4}<br><br><br>L'Équipe Maia</div>""".format(user_data.first_name, patient_name, date, time, notes))

				frappe.sendmail(practitioner_data.user, subject=subject, content=message)
