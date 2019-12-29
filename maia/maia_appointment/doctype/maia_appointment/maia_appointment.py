# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
import re
import json
import requests
from frappe import _
from frappe.model.document import Document
from maia.maia_appointment.scheduler import check_availability
from frappe.utils import getdate, get_time, get_datetime, get_datetime_str, formatdate, now_datetime, add_days, \
	cstr, date_diff, add_months, cint, add_to_date
from frappe.email.doctype.email_template.email_template import get_email_template


weekdays = ["monday", "tuesday", "wednesday",
			"thursday", "friday", "saturday", "sunday"]


class MaiaAppointment(Document):
	def validate(self):
		if self.reminder == 1 and not self.group_event:
			if self.email is None:
				frappe.throw(_("Please enter a valid email address"))

		if self.sms_reminder == 1 and not self.group_event:
			if self.mobile_no is None:
				frappe.throw(_("Please enter a valid mobile number"))
			else:
				valid_number = validate_receiver_no(self.mobile_no)
				if not valid_number[:2] == "00":
					frappe.msgprint(_("The phone number format doesn't seem to match with the allowed formats. Make sure you have added the country code (+33 or 0033) in front else no sms will be sent."))

		if self.personal_event != 1:
			appointment_type = frappe.get_doc("Maia Appointment Type", self.appointment_type)
			if appointment_type.group_appointment == 1 and self.group_event != 1:
				events = get_registration_count(self.appointment_type, self.date)
				inconsistency = 0

				corresponding_events = filter(lambda x: x.start_dt == datetime.datetime.combine(getdate(self.date), get_time(self.start_time)), events)
				if not corresponding_events:
					frappe.throw(_("The date and time of your appointment don't match with the existing group appointments. Please select another slot."))

				else:
					for event in corresponding_events:
						if event.practitioner == self.practitioner:
							if event.seats_left > 0:
								continue
							else:
								frappe.throw(_("The number of participants exceeds the max. number for this group appointment."))
						else:
							inconsistency += 1

				if inconsistency > 0:
					frappe.throw(_("No existing slot could be found for this practitioner, date, time and appointment type."))

	def on_submit(self):
		date = getdate(self.date)
		time = get_time(self.start_time)
		st_dt = datetime.datetime.combine(date, time)
		ed_dt = st_dt + datetime.timedelta(minutes=cint(self.duration))
		frappe.db.set_value("Maia Appointment", self.name, "start_dt", st_dt)
		frappe.db.set_value("Maia Appointment", self.name, "end_dt", ed_dt)
		self.reload()

		if self.reminder == 1 and not self.group_event:
			frappe.db.set_value(
				"Patient Record", self.patient_record, "email_id", self.email)
			self.send_reminder()

		if self.sms_reminder == 1 and not self.group_event:
			if self.mobile_no is not None:
				number = self.mobile_no
			else:
				frappe.throw(_("Please enter a valid mobile number"))
			
			valid_number = validate_receiver_no(number)			
			frappe.db.set_value("Patient Record", self.patient_record, "mobile_no", valid_number)

			self.send_sms_reminder(valid_number)

		if not self.subject:
			self.subject = self.name

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
			reply = get_email_template(self.standard_reply, args)

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

		try:
			if sending_date > now_datetime():
				frappe.sendmail(patient_email, subject=subject,
								content=message, send_after=sending_date)
				self.get_email_id(patient_email, sending_date)
			else:
				frappe.sendmail(patient_email, subject=subject, content=message)
		except Exception as e:
			frappe.log_error(e, "Email reminder sending error")

	def get_email_id(self, patient_email, sending_date):
		email_queue = frappe.get_all("Email Queue")
		queue_id = email_queue[0].name
		frappe.db.set_value("Maia Appointment",
							self.name, "queue_id", queue_id)

	def send_sms_reminder(self, valid_number):
		appointment_date = formatdate(getdate(self.date), "dd/MM/yyyy")
		start_time = get_datetime(self.start_dt).strftime("%H:%M")

		sms_settings = self.get_sms_settings()		

		sr = frappe.new_doc('SMS Reminder')
		sr.sender_name = sms_settings["sender_name"]
		sr.sender = self.practitioner
		sr.send_on = get_datetime(self.start_dt) + datetime.timedelta(days=-cint(sms_settings["send_before"]))
		sr.message = sms_settings["sms_content"].format( midwife=self.practitioner, date=appointment_date, time=start_time)
		sr.send_to = valid_number
		sr.recipient = self.patient_name
		sr.maia_appointment = self.name
		sr.flags.ignore_permissions = True
		sr.save()

	def get_sms_settings(self):
		sms_settings = frappe.db.get_values("Professional Information Card", self.practitioner, \
			["sender_name", "sms_content", "send_before"], as_dict=True)
		
		default_sender = "SageFemme"
		default_content = _("Rappel: Vous avez rendez-vous avec {midwife} le {date} à {time}. En cas d'impossibilité, veuillez contacter votre sage-femme. Merci")
		default_send_before = 1
		
		if sms_settings:
			result = {
				"sender_name": sms_settings[0]["sender_name"] or default_sender,
				"sms_content": sms_settings[0]["sms_content"] or default_content,
				"send_before": sms_settings[0]["send_before"] or default_send_before
			}
		else:
			result = {
				"sender_name": default_sender,
				"sms_content": default_content,
				"send_before": default_send_before
			}

		return result

	def on_cancel(self):
		queue_name = frappe.db.get_value("Maia Appointment", self.name, "queue_id")
		if frappe.db.exists("Email Queue", queue_name):
			try:
				frappe.delete_doc("Email Queue", queue_name, force=True, ignore_permissions=True)
				frappe.db.set_value("Maia Appointment", self.name, "queue_id", "")
			except Exception:
				frappe.log_error(frappe.get_traceback())

		sms_reminder = frappe.get_all("SMS Reminder", filters={"maia_appointment": self.name})
		for sms in sms_reminder:
			try:
				frappe.delete_doc("SMS Reminder", sms.name, force=True, ignore_permissions=True)
			except Exception:
				frappe.log_error(frappe.get_traceback())

		self.reload()

def get_appointment_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by='modified desc'):
	patient = get_patient_record()
	if patient:
		appointments = frappe.db.sql("""select * from `tabMaia Appointment`
			where patient_record = %s order by start_dt desc""", patient, as_dict=True)
	else:
		appointments = frappe.db.sql("""select * from `tabMaia Appointment`
			where user = %s order by start_dt desc""", frappe.session.user, as_dict=True)
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
	frappe.db.set_value("Maia Appointment", appointmentId, "status", status)

@frappe.whitelist()
def get_registration_count(appointment_type, date):
	filters=[["Maia Appointment","appointment_type","=",appointment_type], ["Maia Appointment","group_event","=",1], ["Maia Appointment", "docstatus","=",1]]
	start = get_datetime(date).strftime("%Y-%m-%d %H:%M:%S")
	end = add_to_date(start, years=1)

	at = frappe.get_doc("Maia Appointment Type", appointment_type)

	slots = get_events(start=start, end=end, filters=filters)

	for slot in slots:
		filters = [["Maia Appointment","appointment_type","=",appointment_type], ["Maia Appointment","group_event","=",0], ["Maia Appointment", "docstatus","=",1]]
		start = slot.start_dt.strftime("%Y-%m-%d %H:%M:%S")
		end = slot.end_dt.strftime("%Y-%m-%d %H:%M:%S")
		scheduled_events = get_events(start=start, end=end, filters=filters)

		count = 0
		registered = []
		if scheduled_events:
			for scheduled_event in scheduled_events:
				count += 1
				registered.append({'name': scheduled_event.name, 'patient': scheduled_event.patient_record})

		slot["already_registered"] = count
		slot["number_of_patients"] = at.number_of_patients
		slot["seats_left"] = at.number_of_patients - count
		slot["registered"] = registered

	return slots

@frappe.whitelist()
def get_events(start, end, user=None, filters=None):

	if user:
		practitioner = frappe.db.get_value('Professional Information Card', {'user': frappe.session.user}, 'name')
		if practitioner:
			filters = filters if filters else []
			filters.append(["Maia Appointment","practitioner","=",practitioner])

	from frappe.desk.calendar import get_event_conditions
	add_filters = get_event_conditions("Maia Appointment", filters)

	events = frappe.db.sql("""select name, subject, patient_record, appointment_type, practitioner, color, start_dt, end_dt, duration, repeat_this_event, repeat_on,repeat_till,
		monday, tuesday, wednesday, thursday, friday, saturday, sunday, docstatus from `tabMaia Appointment` where ((
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
				for i in range(int(date_diff(end, start) / 30) + 3):
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

				for cnt in range(int(date_diff(end, start) / 7) + 3):
					if getdate(date) >= getdate(start) and getdate(date) <= getdate(end) \
					   and getdate(date) <= getdate(repeat) and getdate(date) >= getdate(event_start):
						add_event(e, date)

					date = add_days(date, 7)

				remove_events.append(e)

			if e.repeat_on == "Every Day":
				for cnt in range(date_diff(end, start) + 1):
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
def check_availabilities_for_all_practitioners(practitioner, date, duration, appointment_type=None):
	practitioners = frappe.get_all("Professional Information Card", filters=[["name", "!=", practitioner]])
	result =[]
	for practitioner in practitioners:
		availabilities = check_availability_by_midwife(practitioner, date, duration, appointment_type)
		result.append(availabilities)

	return result

@frappe.whitelist()
def check_availability_by_midwife(practitioner, date, duration, appointment_type=None):
	if not (practitioner or date or duration):
		frappe.throw(
			_("Please select a Midwife, a Date and an Appointment Type"))
	if appointment_type is not None:
		group = frappe.db.get_value("Maia Appointment Type", appointment_type, 'group_appointment')
		if group ==1 :
			return 'group_appointment'
		else:
			return _get_availability_by_midwife(practitioner, date, duration)
	else:
		return _get_availability_by_midwife(practitioner, date, duration)

def _get_availability_by_midwife(practitioner, date, duration):
	payload = {}
	payload[practitioner] = check_availability(
		"Maia Appointment",
		"practitioner",
		"Professional Information Card",
		practitioner,
		date,
		duration
	)
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

def flush():
	"""flush email queue, every time: called from scheduler"""
	if frappe.conf.get("sms_activated") == 1:
		sms = frappe.get_all("SMS Reminder", filters={"send_on": ["<", now_datetime()], "status": ["in", ["Queued", "Error"]]}, \
			order_by="creation asc", limit=500)

		for s in sms:
			send_sms_reminder(s["name"])

def send_sms_reminder(name):
	if not frappe.conf.get("customer"):
		frappe.sendmail(recipients="help@dokos.io", subject="SMS customer account missing", \
			content="Missing customer account for site {0}".format(frappe.utils.get_site_base_path().split("/")[1]))
		return frappe.log_error("Missing customer account", "SMS Error")

	if frappe.db.exists("SMS Reminder", name):
		sms = frappe.get_doc("SMS Reminder", name)

		args = {
			"sender": sms.sender_name,
			"content": sms.message,
			"recipient": sms.send_to,
			"type": "transactional",
			"tag": frappe.conf.get("customer")+ "/" + sms.sender,
			"webUrl": "https://dashboard.dokos.io?cmd=dokops.api.sms_callback"
		}

		status = send_request(args)
		if status.status_code in [200, 201, 202, 204]:
			frappe.db.set_value("SMS Reminder", sms.name, "status", "Sent")
			frappe.db.set_value("SMS Reminder", sms.name, "sent_on", now_datetime())
		else:
			status = status.json()
			frappe.db.set_value("SMS Reminder", sms.name, "status", "Error")
			frappe.db.set_value("SMS Reminder", sms.name, "sending_status", status["message"])
			frappe.log_error(status, "SMS Error")

def send_request(data):
	url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
	headers = {
		"content-type": "application/json",
		"api-key": frappe.conf.get("sendinblue_key")
	}
	response = requests.post(url, headers=headers, json=data)
	return response

@frappe.whitelist()
def set_seats_left(appointment, data):
	data = json.loads(data)
	frappe.db.set_value("Maia Appointment", appointment, "seats_left", data['seats_left'])

	if data['seats_left'] > 0:
		return 'green'
	else:
		return 'red'

@frappe.whitelist()
def create_patient_record(data, user):
	data = json.loads(data)
	patient_record = frappe.get_doc({
		"doctype": "Patient Record",
		"patient_first_name": data['first_name'],
		"patient_last_name": data['last_name'],
		"email_id": user,
		"website_user": user
	})

	patient_record.insert(ignore_permissions=True)

	existing_appointments = frappe.get_all("Maia Appointment", filters={"user": user, "patient_record": ""})
	for appointment in existing_appointments:
		frappe.db.set_value("Maia Appointment", appointment.name, "patient_record", patient_record.name)

	return 'success'
