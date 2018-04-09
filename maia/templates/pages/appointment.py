# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint, get_datetime, add_days, formatdate, get_datetime_str
from frappe import _
import datetime
from datetime import timedelta, date
import calendar
from maia.maia_appointment.scheduler import get_availability_from_schedule

def get_context(context):
	context.no_cache = 1

@frappe.whitelist()
def get_practitioners_and_appointment_types():
	practitioners = frappe.get_list("Professional Information Card", filters={"allow_online_booking": 1}, fields=['name', 'weekend_booking'])

	if practitioners:
		results = []
		for practitioner in practitioners:
			result = {}
			result.update({'name': practitioner['name'], 'week_end': practitioner['weekend_booking']})
			appointment_types = frappe.db.sql("""SELECT appointment_type, name, group_appointment, number_of_patients, description from `tabMaia Appointment Type` WHERE allow_online_booking=1 AND (practitioner='{0}' OR practitioner IS NULL)""".format(practitioner.name), as_dict=True)
			at = []
			for appointment_type in appointment_types:
				at.append({'name': appointment_type.name, 'appointment_type': appointment_type.appointment_type, 'group_appointment': appointment_type.group_appointment, 'number_of_patients': appointment_type.number_of_patients, 'description': appointment_type.description})

			result.update({'appointment_types': at})
			results.append(result)

		return results

	else:
		return []

def daterange(start_date, end_date):
	if start_date < now_datetime():
		start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
	for n in range(int((end_date - start_date).days)):
		yield start_date + timedelta(n)

@frappe.whitelist()
def check_availabilities(practitioner, start, end, appointment_type):
	duration = frappe.get_value("Maia Appointment Type", dict(appointment_type=appointment_type), "duration")

	start = datetime.datetime.strptime(start, '%Y-%m-%d')
	end = datetime.datetime.strptime(end, '%Y-%m-%d')
	days_limit = frappe.get_value("Professional Information Card", practitioner, "number_of_days_limit")
	limit = datetime.datetime.combine(add_days(getdate(), int(days_limit)), datetime.datetime.time(datetime.datetime.now()))

	payload = []
	if start < limit:
		for dt in daterange(start, end):
			date = dt.strftime("%Y-%m-%d")

			calendar_availability = _check_availability("Maia Appointment", "practitioner", "Professional Information Card", practitioner, date, duration)
			if bool(calendar_availability) == True:
				payload += calendar_availability

	avail = []
	for items in payload:
		avail += items

	final_avail = []
	final_avail.append(avail)

	return final_avail

def _check_availability(doctype, df, dt, dn, date, duration):
	date = getdate(date)
	day = calendar.day_name[date.weekday()]
	if date < getdate():
		pass

	resource = frappe.get_doc(dt, dn)
	availability = []
	schedules = []

	if hasattr(resource, "consulting_schedule") and resource.consulting_schedule:
		day_sch = filter(lambda x: x.day == day, resource.consulting_schedule)
		if not day_sch:
			return availability

		for line in day_sch:
			if(datetime.datetime.combine(date, get_time(line.end_time)) > now_datetime()):
				schedules.append({"start": datetime.datetime.combine(date, get_time(line.start_time)), "end": datetime.datetime.combine(
					date, get_time(line.end_time)), "duration": datetime.timedelta(minutes=cint(duration))})

			if schedules:
				availability.extend(get_availability_from_schedule(doctype, df, dn, schedules, date))

	return availability

@frappe.whitelist()
def submit_appointment(email, practitioner, appointment_type, start, end, notes):
	frappe.log_error(email, "email")
	frappe.log_error(practitioner, "practitioner")
	frappe.log_error(appointment_type, "appointment_type")
	frappe.log_error(start, "start")
	frappe.log_error(end, "end")
	frappe.log_error(notes, "notes")

	start_date = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').date()
	start_time = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').time()
	app_type = frappe.get_doc("Maia Appointment Type", appointment_type)

	sms_confirmation = app_type.send_sms_reminder

	patient_records = frappe.get_all("Patient Record", filters={
									 'website_user': email}, fields=['name', 'mobile_no'])
	if not patient_records:
		user = frappe.get_doc("User", email)
		patient_record = ""
		if user.last_name:
			subject = "{0} {1}-En Ligne".format(
				user.first_name, user.last_name)
		else:
			subject = "{0}-En Ligne".format(user.first_name)
		sms_confirmation = 0
		mobile_no = ""

	else:
		patient_record = patient_records[0].name
		subject = "{0}-En Ligne".format(patient_record)
		mobile_no = patient_records[0].mobile_no
		if sms_confirmation == 1 and mobile_no:
			sms_confirmation = 1
		else:
			sms_confirmation = 0

	appointment_type = frappe.get_doc("Maia Appointment Type", dict(appointment_type=appointment_type))

	appointment = frappe.get_doc({
		"doctype": "Maia Appointment",
		"patient_record": patient_record,
		"practitioner": practitioner,
		"appointment_type": appointment_type.name,
		"date": start_date,
		"start_time": start_time,
		"start_dt": start,
		"end_dt": end,
		"duration": app_type.duration,
		"color": app_type.color,
		"subject": subject,
		"notes": notes,
		"reminder": 1,
		"email": email,
		"sms_reminder": sms_confirmation,
		"mobile_no": mobile_no
	}).insert()
	appointment.flags.ignore_mandatory = True
	appointment.submit()

	if patient_record:
		send_patient_confirmation(
			patient_record, practitioner, appointment_type.name, start)
		send_notification_for_patient(
			patient_record, practitioner, appointment_type.name, start, notes)

	else:
		send_user_confirmation(user, practitioner, appointment_type.name, start)
		send_notification_for_user(
			user, practitioner, appointment_type.name, start, notes)

	frappe.clear_cache()

	return "OK"


def send_patient_confirmation(patient_record, practitioner, appointment_type, start):
	from frappe.utils import get_url
	patient = frappe.get_doc("Patient Record", patient_record)
	date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
	time = get_datetime(start).strftime("%H:%M")
	link = get_url("/login")

	subject = _(
		"""Confirmation de votre rendez-vous avec {0}""".format(practitioner))
	message = _("""<div>Bonjour {0},<br><br>Votre rendez-vous ""{1}"" est confirmé le {2}, à {3}.<br><br>Pour toute annulation jusqu'à 48H avant le rendez-vous, veuillez cliquer <a href="{4}">ici.</a><br><br>En cas d'empêchement dans les dernières 48H, veuillez me contacter.<br><br>Merci beaucoup.<br><br>{5}</div>""".format(
		patient.patient_first_name, appointment_type, date, time, link, practitioner))

	if patient.email_id == None:
		frappe.sendmail(patient.website_user, subject=subject, content=message)
	else:
		frappe.sendmail(patient.email_id, subject=subject, content=message)


def send_user_confirmation(user, practitioner, appointment_type, start):
	from frappe.utils import get_url
	date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
	time = get_datetime(start).strftime("%H:%M")
	link = get_url("/login")

	subject = _(
		"""Confirmation de votre rendez-vous avec {0}""".format(practitioner))
	message = _("""<div>Bonjour {0},<br><br>Votre rendez-vous ""{1}"" est confirmé le {2}, à {3}.<br><br>Pour toute annulation jusqu'à 48H avant le rendez-vous, veuillez cliquer <a href="{4}">ici.</a><br><br>En cas d'empêchement dans les dernières 48H, veuillez me contacter.<br><br>Merci beaucoup.<br><br>{5}</div>""".format(
		user.first_name, appointment_type, date, time, link, practitioner))

	frappe.sendmail(user.email, subject=subject, content=message)


def send_notification_for_patient(patient_record, practitioner, appointment_type, start, notes):
	patient = frappe.get_doc("Patient Record", patient_record)
	practitioner_data = frappe.get_doc(
		"Professional Information Card", practitioner)
	if practitioner_data.user:
		user_data = frappe.get_doc("User", practitioner_data.user)
		date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
		time = get_datetime(start).strftime("%H:%M")

		subject = _("""[Maia] Nouveau Rendez-Vous en Ligne""")
		message = _("""<div>Bonjour {0},<br><br>{1} vient de prendre rendez-vous sur votre plateforme de réservation.<br><br><strong>Date:</strong> {2}<br><br><strong>Heure:</strong> {3}<br><br><strong>Type de Rendez-Vous:</strong> {4}<br><br><strong>Message:</strong> {5}<br><br><br>L'Équipe Maia</div>""".format(
			user_data.first_name, patient.name, date, time, appointment_type, notes))

		frappe.sendmail(practitioner_data.user,
						subject=subject, content=message)


def send_notification_for_user(user, practitioner, appointment_type, start, notes):
	practitioner_data = frappe.get_doc(
		"Professional Information Card", practitioner)
	if practitioner_data.user:
		user_data = frappe.get_doc("User", practitioner_data.user)
		date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
		time = get_datetime(start).strftime("%H:%M")

		subject = _("""[Maia] Nouveau Rendez-Vous en Ligne""")
		if user.last_name:
			message = _("""<div>Bonjour {0},<br><br>{1} {2} vient de prendre rendez-vous sur votre plateforme de réservation.<br><br><strong>Date:</strong> {3}<br><br><strong>Heure:</strong> {4}<br><br><strong>Type de Rendez-Vous:</strong> {5}<br><br><strong>Message:</strong> {6}<br><br><br>L'Équipe Maia</div>""".format(
				user_data.first_name, user.first_name, user.last_name, date, time, appointment_type, notes))
		else:
			message = _("""<div>Bonjour {0},<br><br>{1} vient de prendre rendez-vous sur votre plateforme de réservation.<br><br><strong>Date:</strong> {2}<br><br><strong>Heure:</strong> {3}<br><br><strong>Type de Rendez-Vous:</strong> {4}<br><br><strong>Message:</strong> {5}<br><br><br>L'Équipe Maia</div>""".format(
				user_data.first_name, user.first_name, date, time,  appointment_type, notes))

		frappe.sendmail(practitioner_data.user,
						subject=subject, content=message)
