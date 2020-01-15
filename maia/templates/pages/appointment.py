# -*- coding: utf-8 -*-
# Copyright (c) 2020, DOKOS SAS
# See license.txt

import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint, get_datetime, add_days, formatdate, get_datetime_str, add_to_date, get_time_zone
from frappe import _
import datetime
from datetime import timedelta, date
import calendar
from maia.maia_appointment.scheduler import ScheduleAvailability
from maia.maia_appointment.doctype.maia_appointment.maia_appointment import get_registration_count
from collections import defaultdict
from maia.utilities.utils import daterange

def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	if not "Patient" in frappe.get_roles(frappe.session.user):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

@frappe.whitelist()
def get_practitioners_and_appointment_types():
	practitioners = frappe.get_list("Professional Information Card", filters={"allow_online_booking": 1}, fields=['name', 'weekend_booking'])

	if practitioners:
		results = []
		for practitioner in practitioners:
			result = {}
			result.update({'name': practitioner['name'], 'week_end': practitioner['weekend_booking'], 'timezone': get_time_zone()})
			appointment_types = frappe.db.sql("""SELECT appointment_type, name, group_appointment, number_of_patients, description, category FROM `tabMaia Appointment Type` WHERE allow_online_booking=1 AND disabled=0 AND (practitioner='{0}' OR practitioner IS NULL) ORDER BY appointment_type""".format(practitioner.name), as_dict=True)

			d = defaultdict(list)
			categories = set()
			for appointment_type in appointment_types:
				key = appointment_type.category
				if key is None:
					key = _("Without Category")
				categories.add(key)
				d[key].append({'name': appointment_type.name, 'appointment_type': appointment_type.appointment_type, 'group_appointment': appointment_type.group_appointment, 'number_of_patients': appointment_type.number_of_patients, 'description': appointment_type.description, 'category': appointment_type.category})

			result.update({'categories': sorted(list(categories))})
			result.update({'appointment_types': d})
			results.append(result)

		return results

	else:
		return []

@frappe.whitelist()
def check_availabilities(practitioner, start, end, appointment_type):
	availability = MaiaAvailability(practitioner, start, end, appointment_type)
	return availability.get_availability()

class MaiaAvailability():
	def __init__(self, practitioner, start, end, appointment_type):
		self.practitioner = practitioner
		self.start = datetime.datetime.strptime(start, '%Y-%m-%d')
		self.end = datetime.datetime.strptime(end, '%Y-%m-%d')
		self.appointment_type = appointment_type
		self.duration = frappe.get_value("Maia Appointment Type", self.appointment_type, "duration")
		limit_in_days = frappe.get_value("Professional Information Card", practitioner, "number_of_days_limit") or 0
		self.limit = datetime.datetime.combine(add_days(getdate(), int(limit_in_days)), datetime.datetime.time(datetime.datetime.now()))

	def get_availability(self):
		if self.duration is not None:
			payload = []
			if self.start < self.limit:
				for dt in daterange(self.start, self.end):
					date = getdate(dt.strftime("%Y-%m-%d"))

					calendar_availability = self._get_availability(date)
					if bool(calendar_availability) == True:
						payload += calendar_availability

			result = []
			for items in payload:
				result += items

			return result

	def _get_availability(self, date):
		day = calendar.day_name[date.weekday()]
		if ((date < getdate()) or (date == add_to_date(getdate(), days=1) and nowtime() > "19:00")):
			return

		resource = frappe.get_cached_doc("Maia Appointment Type", self.appointment_type)
		if not getattr(resource, "consulting_schedule"):
			resource = frappe.get_cached_doc("Professional Information Card", self.practitioner)

		availability = []
		schedules = []

		if getattr(resource, "consulting_schedule"):
			daily_schedule = list(filter(lambda x: x.day == day, resource.consulting_schedule))
			if not daily_schedule:
				return availability

			for line in daily_schedule:
				if(datetime.datetime.combine(date, get_time(line.end_time)) > now_datetime()):
					schedules.append({
						"start": datetime.datetime.combine(date, get_time(line.start_time)),
						"end": datetime.datetime.combine(date, get_time(line.end_time)),
						"duration": datetime.timedelta(minutes=cint(self.duration))
					})

			if schedules:
				schedule_availability = ScheduleAvailability(self.practitioner, schedules, date)
				availability.append(schedule_availability.get_availabilities())

		return availability

@frappe.whitelist()
def get_next_availability(practitioner, appointment_type, start, is_group):
	start = get_datetime(start)
	end = start + timedelta(days=1)
	days_limit = frappe.get_value("Professional Information Card", practitioner, "number_of_days_limit")
	limit = datetime.datetime.combine(add_days(getdate(), int(days_limit)), datetime.datetime.time(datetime.datetime.now()))
	slots = []

	while not slots and start < limit:
		if cint(is_group) == 1:
			avail = check_group_events_availabilities(practitioner, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), appointment_type)
			if avail:
				slots = avail
			else:
				start, end = _increment_start_end(practitioner, start, end)
		else:
			avail = check_availabilities(practitioner, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), appointment_type)
			if avail and avail[0]:
				slots = avail
			else:
				start, end = _increment_start_end(practitioner, start, end)

	if start >= limit:
		return {"status": 201, "date": limit}
	else:
		return {"status": 200, "date": start}

@frappe.whitelist()
def check_group_events_availabilities(practitioner, start, end, appointment_type):
	if (datetime.datetime.strptime(start, '%Y-%m-%d') > get_datetime()):
		start = datetime.datetime.strptime(start, '%Y-%m-%d')
	elif (datetime.datetime.strptime(start, '%Y-%m-%d') <= get_datetime()) and (nowtime() > "19:00"):
		start = get_datetime().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)
	else:
		start = get_datetime().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

	end = datetime.datetime.strptime(end, '%Y-%m-%d')
	days_limit = frappe.get_value("Professional Information Card", practitioner, "number_of_days_limit")
	limit = datetime.datetime.combine(add_days(getdate(), int(days_limit)), datetime.datetime.time(datetime.datetime.now()))

	payload = []
	slots = []
	if start < limit:
		for dt in daterange(start, end):
			slots = get_registration_count(appointment_type, start)

			slots = filter(lambda x: x.practitioner == practitioner, slots)
			slots = filter(lambda x: x.seats_left > 0, slots)
			slots = filter(lambda x: x.start_dt < end, slots)
			slots = [{**{k: v for k, v in x.items() if k != "color"}, "start": x.get("start_dt"), "end": x.get("end_dt"), "id": x.get("name")} for x in list(slots)]

	return slots

def _increment_start_end(practitioner, start, end):
	week_end_bookings = frappe.get_value("Professional Information Card", practitioner, "weekend_booking")
	if week_end_bookings:
		start = start + timedelta(days=1)
		end = end + timedelta(days=1)
	else:
		wkday = start.weekday()
		if wkday == 4:
			start = start + timedelta(days=3)
			end = end + timedelta(days=3)
		else:
			start = start + timedelta(days=1)
			end = end + timedelta(days=1)

	return start, end

@frappe.whitelist()
def submit_appointment(email, practitioner, appointment_type, start, end, notes):
	# For developments
	if email == "Administrator":
		email = "oli.celine@hotmail.fr"

	start_date = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').date()
	start_time = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').time()
	app_type = frappe.get_doc("Maia Appointment Type", appointment_type)

	sms_confirmation = app_type.send_sms_reminder

	patient_records = frappe.get_all("Patient Record", filters={'website_user': email}, fields=['name', 'mobile_no'])
	user = frappe.get_doc("User", email)

	if not patient_records:
		patient_record = None
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

	appointment = frappe.get_doc({
		"doctype": "Maia Appointment",
		"patient_record": patient_record,
		"status": "Confirmed",
		"user": user.name,
		"practitioner": practitioner,
		"appointment_type": app_type.name,
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

	if patient_record:
		send_patient_confirmation(patient_record, practitioner, app_type.name, start)
		send_notification_for_patient(patient_record, practitioner, app_type.name, start, notes)

	else:
		send_user_confirmation(user, practitioner, app_type.name, start)
		send_notification_for_user(user, practitioner, app_type.name, start, notes)

	frappe.clear_cache()

	return "OK"


def send_patient_confirmation(patient_record, practitioner, appointment_type, start):
	from frappe.utils import get_url
	patient = frappe.get_doc("Patient Record", patient_record)
	date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
	time = get_datetime(start).strftime("%H:%M")
	link = get_url("/login")
	app_type = frappe.get_doc("Maia Appointment Type", appointment_type)

	subject = _("""Confirmation de votre rendez-vous avec {0}""".format(practitioner))
	message = _("""<div>Bonjour {0},<br><br>Votre rendez-vous ""{1}"" est confirmé le {2}, à {3}.<br><br>Pour toute annulation jusqu'à 48H avant le rendez-vous, veuillez cliquer <a href="{4}">ici.</a><br><br>En cas d'empêchement dans les dernières 48H, veuillez me contacter.<br><br>Merci beaucoup.<br><br>{5}</div>""".format(
		patient.patient_first_name, app_type.appointment_type, date, time, link, practitioner))

	if patient.email_id == None:
		frappe.sendmail(patient.website_user, subject=subject, content=message)
	else:
		frappe.sendmail(patient.email_id, subject=subject, content=message)

def send_user_confirmation(user, practitioner, appointment_type, start):
	from frappe.utils import get_url
	date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
	time = get_datetime(start).strftime("%H:%M")
	link = get_url("/login")
	app_type = frappe.get_doc("Maia Appointment Type", appointment_type)

	subject = _("""Confirmation de votre rendez-vous avec {0}""".format(practitioner))
	message = _("""<div>Bonjour {0},<br><br>Votre rendez-vous ""{1}"" est confirmé le {2}, à {3}.<br><br>Pour toute annulation jusqu'à 48H avant le rendez-vous, veuillez cliquer <a href="{4}">ici.</a><br><br>En cas d'empêchement dans les dernières 48H, veuillez me contacter.<br><br>Merci beaucoup.<br><br>{5}</div>""".format(
		user.first_name, app_type.appointment_type, date, time, link, practitioner))

	frappe.sendmail(user.email, subject=subject, content=message)

def send_notification_for_patient(patient_record, practitioner, appointment_type, start, notes):
	patient = frappe.get_doc("Patient Record", patient_record)
	app_type = frappe.get_doc("Maia Appointment Type", appointment_type)
	practitioner_data = frappe.get_doc("Professional Information Card", practitioner)
	if practitioner_data.user:
		user_data = frappe.get_doc("User", practitioner_data.user)
		date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
		time = get_datetime(start).strftime("%H:%M")

		subject = _("""[Maia] Nouveau Rendez-Vous en Ligne""")
		message = _("""<div>Bonjour {0},<br><br>{1} vient de prendre rendez-vous sur votre plateforme de réservation.<br><br><strong>Date:</strong> {2}<br><br><strong>Heure:</strong> {3}<br><br><strong>Type de Rendez-Vous:</strong> {4}<br><br><strong>Message:</strong> {5}<br><br><br>L'Équipe Maia</div>""".format(
			user_data.first_name, patient.name, date, time, app_type.appointment_type, notes))

		frappe.sendmail(practitioner_data.user, subject=subject, content=message)

def send_notification_for_user(user, practitioner, appointment_type, start, notes):
	practitioner_data = frappe.get_doc("Professional Information Card", practitioner)
	app_type = frappe.get_doc("Maia Appointment Type", appointment_type)
	if practitioner_data.user:
		user_data = frappe.get_doc("User", practitioner_data.user)
		date = formatdate(get_datetime_str(start), "dd/MM/yyyy")
		time = get_datetime(start).strftime("%H:%M")

		subject = _("""[Maia] Nouveau Rendez-Vous en Ligne""")
		if user.last_name:
			message = _("""<div>Bonjour {0},<br><br>{1} {2} vient de prendre rendez-vous sur votre plateforme de réservation.<br><br><strong>Date:</strong> {3}<br><br><strong>Heure:</strong> {4}<br><br><strong>Type de Rendez-Vous:</strong> {5}<br><br><strong>Message:</strong> {6}<br><br><br>L'Équipe Maia</div>""".format(
				user_data.first_name, user.first_name, user.last_name, date, time, app_type.appointment_type, notes))
		else:
			message = _("""<div>Bonjour {0},<br><br>{1} vient de prendre rendez-vous sur votre plateforme de réservation.<br><br><strong>Date:</strong> {2}<br><br><strong>Heure:</strong> {3}<br><br><strong>Type de Rendez-Vous:</strong> {4}<br><br><strong>Message:</strong> {5}<br><br><br>L'Équipe Maia</div>""".format(
				user_data.first_name, user.first_name, date, time,  app_type.appointment_type, notes))

		frappe.sendmail(practitioner_data.user, subject=subject, content=message)
