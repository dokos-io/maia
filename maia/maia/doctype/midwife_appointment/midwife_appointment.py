# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.scheduler import check_availability
from frappe import _
import datetime
from frappe.utils import getdate, get_time, get_datetime, get_datetime_str, formatdate, now_datetime, add_days, nowdate, cstr, date_diff, add_months, cint
from frappe.email.doctype.standard_reply.standard_reply import get_standard_reply
from mailin import Mailin
import re

weekdays = ["monday", "tuesday", "wednesday",
			"thursday", "friday", "saturday", "sunday"]


class MidwifeAppointment(Document):
	def validate(self):
		if self.reminder == 1:
			if self.email is None:
				frappe.throw(_("Please enter a valid email address"))

		if self.sms_reminder == 1:
			if self.mobile_no is None:
				frappe.throw(_("Please enter a valid mobile number"))
	def on_submit(self):
		date = getdate(self.date)
		time = get_time(self.start_time)
		st_dt = datetime.datetime.combine(date, time)
		ed_dt = st_dt + datetime.timedelta(minutes=int(self.duration))
		frappe.db.set_value("Midwife Appointment",
							self.name, "start_dt", st_dt)
		frappe.db.set_value("Midwife Appointment", self.name, "end_dt", ed_dt)
		self.reload()

		if self.reminder == 1:
			frappe.db.set_value(
				"Patient Record", self.patient_record, "email_id", self.email)
			self.send_reminder()

		if self.sms_reminder == 1:
			if self.mobile_no is not None:
				number = self.mobile_no
			else:
				frappe.throw(_("Please enter a valid mobile number"))
			valid_number = validate_receiver_no(number)

			frappe.db.set_value(
				"Patient Record", self.patient_record, "mobile_no", valid_number)

			self.send_sms_reminder(valid_number)

	def send_reminder(self):
		patient_email = self.email
		sending_date = get_datetime(self.start_dt) + datetime.timedelta(days=-1)

		if self.standard_reply:
			args = {
				"patient_record": self.patient_record,
				"patient_first_name": frappe.db.get_value("Patient Record", self.patient_record, "patient_first_name"),
				"patient_last_name": frappe.db.get_value("Patient Record", self.patient_record, "patient_last_name"),
				"practitioner": self.practitioner,
				"appointment_type": self.appointment_type,
				"patient_name": self.patient_name,
				"date": formatdate(get_datetime_str(self.start_dt), "dd/MM/yyyy"),
				"start_time": get_datetime(self.start_dt).strftime("%H:%M"),
				"standard_reply": self.standard_reply,
				"duration": self.duration
			}
			reply = get_standard_reply(self.standard_reply, args)

			subject = reply["subject"]
			message = reply["message"]
		else:
			if self.patient_record:
				patient_first_name = frappe.db.get_value(
					"Patient Record", self.patient_record, "patient_first_name")
			else:
				patient_first_name = frappe.db.get_value(
					"User", self.email, "first_name")
			appointment_date = formatdate(getdate(self.date), "dd/MM/yyyy")
			start_time = get_datetime(self.start_dt).strftime("%H:%M")

			subject = _("""N'oubliez pas votre rendez-vous avec {0}, prévu le {1} à {2}""".format(
				self.practitioner, appointment_date, start_time))
			message = _("""Bonjour {0}, <br><br>Votre rendez-vous est toujours prévu le {1}, à {2}. <br><br>Si vous avez un empêchement, veuillez me l'indiquer au plus vite par retour de mail.<br><br>Merci beaucoup.<br><br>{3}""".format(
				patient_first_name, appointment_date, start_time, self.practitioner))

		if sending_date > now_datetime():
			frappe.sendmail(patient_email, subject=subject,
							content=message, send_after=sending_date)
			self.get_email_id(patient_email, sending_date)
		else:
			frappe.sendmail(patient_email, subject=subject, content=message)

	def get_email_id(self, patient_email, sending_date):
		email_queue = frappe.get_all("Email Queue")
		queue_id = email_queue[0].name
		frappe.db.set_value("Midwife Appointment",
							self.name, "queue_id", queue_id)

	def send_sms_reminder(self, valid_number):
		send_after_day = get_datetime(self.start_dt) + datetime.timedelta(days=-1)
		appointment_date = formatdate(getdate(self.date), "dd/MM/yyyy")
		start_time = get_datetime(self.start_dt).strftime("%H:%M")

		sr = frappe.new_doc('SMS Reminder')
		sr.sender_name = self.practitioner
		sr.sender = self.practitioner
		sr.send_on = send_after_day
		sr.message = _("""Rappel: Vous avez rendez-vous avec {0} le {1} à {2}. En cas d'impossibilité, veuillez contacter votre sage-femme. Merci""".format(
			self.practitioner, appointment_date, start_time))
		sr.send_to = valid_number
		sr.midwife_appointment = self.name
		sr.flags.ignore_permissions = True
		sr.save()

	def on_cancel(self):
		queue_name = frappe.db.get_value(
			"Midwife Appointment", self.name, "queue_id")
		if frappe.db.exists("Email Queue", queue_name):
			frappe.delete_doc("Email Queue", queue_name,
							  ignore_permissions=True)
		frappe.db.set_value("Midwife Appointment", self.name, "queue_id", "")

		sms_reminder = frappe.get_all("SMS Reminder", filters={
									  "midwife_appointment": self.name})

		for sms in sms_reminder:
			frappe.delete_doc("SMS Reminder", sms.name,
							  ignore_permissions=True)

		self.reload()


def get_appointment_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by='modified desc'):
	patient = get_patient_record()
	if patient:
		appointments = frappe.db.sql("""select * from `tabMidwife Appointment`
			where patient_record = %s order by start_dt desc""", patient, as_dict=True)
	else:
		appointments = frappe.db.sql("""select * from `tabMidwife Appointment`
			where email = %s order by start_dt desc""", frappe.session.user, as_dict=True)
	return appointments

def get_patient_record():
	return frappe.get_value("Patient Record",{"website_user": frappe.session.user}, "name")

def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		'no_breadcrumbs': True,
		"title": _("My Appointments"),
		"get_list": get_appointment_list,
		"row_template": "templates/includes/appointments/appointment_row.html"
	}

@frappe.whitelist()
def update_status(appointmentId, status):
	frappe.db.set_value("Midwife Appointment", appointmentId, "status", status)


@frappe.whitelist()
def get_events(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	add_filters = get_event_conditions("Midwife Appointment", filters)

	events = frappe.db.sql("""select name, subject, patient_record, appointment_type, color, start_dt, end_dt, duration, repeat_this_event, repeat_on,repeat_till,
		monday, tuesday, wednesday, thursday, friday, saturday, sunday from `tabMidwife Appointment` where ((
		(date(start_dt) between date(%(start)s) and date(%(end)s))
		or (date(end_dt) between date(%(start)s) and date(%(end)s))
		or (date(start_dt) <= date(%(start)s) and date(end_dt) >= date(%(end)s))
		) or (
		date(start_dt) <= date(%(start)s) and repeat_this_event=1 and
		ifnull(repeat_till, "3000-01-01") >= date(%(start)s)
		))and docstatus < 2 {add_filters}""".format(add_filters=add_filters), {
		"start": start,
		"end": end
	}, as_dict=True, update={"allDay": 0})

	# process recurring events
	start = start.split(" ")[0]
	end = end.split(" ")[0]
	add_events = []
	remove_events = []

	def add_event(e, date):
		new_event = e.copy()

		enddate = add_days(date, int(date_diff(e.end_dt.split(" ")[0], e.start_dt.split(" ")[0]))) \
			if (e.start_dt and e.end_dt) else date
		new_event.start_dt = date + " " + e.start_dt.split(" ")[1]
		if e.end_dt:
			new_event.end_dt = enddate + " " + e.end_dt.split(" ")[1]
		add_events.append(new_event)

	for e in events:
		if e.repeat_this_event:
			e.start_dt = get_datetime_str(e.start_dt)
			if e.end_dt:
				e.end_dt = get_datetime_str(e.end_dt)

			event_start, time_str = get_datetime_str(e.start_dt).split(" ")
			if cstr(e.repeat_till) == "":
				repeat = "3000-01-01"
			else:
				repeat = e.repeat_till
			if e.repeat_on == "Every Year":
				start_year = cint(start.split("-")[0])
				end_year = cint(end.split("-")[0])
				event_start = "-".join(event_start.split("-")[1:])

				# repeat for all years in period
				for year in range(start_year, end_year + 1):
					date = str(year) + "-" + event_start
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) and getdate(date) <= getdate(repeat):
						add_event(e, date)

				remove_events.append(e)

			if e.repeat_on == "Every Month":
				date = start.split(
					"-")[0] + "-" + start.split("-")[1] + "-" + event_start.split("-")[2]

				# last day of month issue, start from prev month!
				try:
					getdate(date)
				except ValueError:
					date = date.split("-")
					date = date[0] + "-" + \
						str(cint(date[1]) - 1) + "-" + date[2]

				start_from = date
				for i in xrange(int(date_diff(end, start) / 30) + 3):
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
					   and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
						add_event(e, date)
					date = add_months(start_from, i + 1)

				remove_events.append(e)

			if e.repeat_on == "Every Week":
				weekday = getdate(event_start).weekday()
				# monday is 0
				start_weekday = getdate(start).weekday()

				# start from nearest weeday after last monday
				date = add_days(start, weekday - start_weekday)

				for cnt in xrange(int(date_diff(end, start) / 7) + 3):
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
					   and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
						add_event(e, date)

					date = add_days(date, 7)

				remove_events.append(e)

			if e.repeat_on == "Every Day":
				for cnt in xrange(date_diff(end, start) + 1):
					date = add_days(start, cnt)
					if getdate(date) >= getdate(event_start) and getdate(date) <= getdate(end) \
					   and getdate(date) <= getdate(repeat) and e[weekdays[getdate(date).weekday()]]:
						add_event(e, date)
				remove_events.append(e)

	for e in remove_events:
		events.remove(e)

	events = events + add_events

	for e in events:
		# remove weekday properties (to reduce message size)
		for w in weekdays:
			del e[w]

	return events


@frappe.whitelist()
def check_availability_by_midwife(practitioner, date, duration):
	if not (practitioner or date or duration):
		frappe.throw(
			_("Please select a Midwife, a Date and an Appointment Type"))
	payload = {}
	payload[practitioner] = check_availability(
		"Midwife Appointment", "practitioner", "Professional Information Card", practitioner, date, duration)
	if payload[practitioner] == [[]]:
		payload[practitioner] = []
	return payload


def validate_receiver_no(validated_no):

	for x in [' ', '-', '(', ')', '.']:
		validated_no = validated_no.replace(x, '')
	for y in ['+']:
		validated_no = validated_no.replace(y, '00')

	if not validated_no:
		frappe.throw(_("Please enter a valid mobile number"))

	return validated_no


def flush(from_test=False):
	"""flush email queue, every time: called from scheduler"""
	if frappe.conf.get("sms_activated") == 1:
		# additional check
		cache = frappe.cache()

		auto_commit = not from_test

		make_cache_queue()

		for i in range(cache.llen('cache_sms_queue')):
			sms = cache.lpop('cache_sms_queue')

			if sms:
				send_sms_reminder(sms)


def make_cache_queue():
	'''cache values in queue before sending'''
	cache = frappe.cache()

	sms = frappe.db.sql('''select
		name
		from `tabSMS Reminder`
		where send_on < %(now)s
		order by creation asc
		limit 500''', {'now': now_datetime()})

	# reset value
	cache.delete_value('cache_sms_queue')
	for e in sms:
		cache.rpush('cache_sms_queue', e[0])


def send_sms_reminder(name):
	sms = frappe.db.sql('''select
		name, sender_name, sender, send_on, message, send_to
		from
		`tabSMS Reminder`
		where
		name=%s
		for update''', name, as_dict=True)[0]

	args = {"text": sms.message}
	args["from"] = "SageFemme"
	args["to"] = sms.send_to
	args["type"] = "transactional"
	args["tag"] = frappe.conf.get("customer")+ "/" + sms.sender
	args["practitioner"] = sms.sender
	status = send_request(args)

	if status["code"] == "success":
		create_sms_log(args)
		reminder = frappe.get_doc('SMS Reminder', sms.name)
		reminder.delete()

	else:
		frappe.log_error(status, "Erreur SMS: " + sms.name)


def send_request(params):
	sendinblue_key = frappe.conf.get("sendinblue_key")
	m = Mailin("https://api.sendinblue.com/v2.0", sendinblue_key)
	data = params
	result = m.send_sms(data)
	return result


def create_sms_log(args):
	sl = frappe.new_doc('SMS Log')
	sl.sender_name = args['practitioner']
	sl.sent_on = nowdate()
	sl.message = args['text']
	sl.no_of_requested_sms = 1
	sl.requested_numbers = "\n".join(args['to'])
	sl.no_of_sent_sms = 1
	sl.sent_to = "\n".join(args['to'])
	sl.flags.ignore_permissions = True
	sl.save()
