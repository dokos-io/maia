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
from frappe.integrations.doctype.google_calendar.google_calendar import get_google_calendar_object, \
	format_date_according_to_google_calendar, get_timezone_naive_datetime
from googleapiclient.errors import HttpError
from frappe.desk.calendar import process_recurring_events

class MaiaAppointment(Document):
	def validate(self):
		self.validate_end_date()
		self.validate_user_email()
		self.validate_user_phone()
		self.validate_group_participants()
		self.validate_filled_information()

	def validate_end_date(self):
		if getdate(self.end_dt) < getdate(self.start_dt):
			frappe.throw(_("End date must be after or equal to start date."))

	def validate_user_email(self):
		if self.reminder == 1 and not self.group_event:
			if self.email is None:
				frappe.throw(_("Please enter a valid email address"))

	def validate_user_phone(self):
		if self.sms_reminder == 1 and not self.group_event:
			if self.mobile_no is None:
				frappe.throw(_("Please enter a valid mobile number"))
			else:
				valid_number = validate_receiver_no(self.mobile_no)
				if not valid_number[:2] == "00":
					frappe.msgprint(_("The phone number format doesn't seem to match with the allowed formats. Make sure you have added the country code (+33 or 0033) in front else no sms will be sent."))

	def validate_filled_information(self):
		if self.sync_with_google_calendar and not self.google_calendar:
			self.google_calendar = frappe.db.get_value("Professional Information Card", self.practitioner, "google_calendar")

		if self.google_calendar and not self.google_calendar_id:
			self.google_calendar_id = frappe.db.get_value("Google Calendar", self.google_calendar, "google_calendar_id")

		if isinstance(self.rrule, list) and self.rrule > 1:
			self.rrule = self.rrule[0]

		if not self.practitioner_user:
			self.practitioner_user = frappe.db.get_value("Professional Information Card", self.practitioner, "user")

		if not self.subject:
			self.subject = self.name

		if not self.user and self.patient_record:
			self.user = frappe.db.get_value("Patient Record", self.patient_record, "website_user")

	def validate_group_participants(self):
		if self.personal_event != 1 and self.group_event != 1 and frappe.get_doc("Maia Appointment Type", self.appointment_type, "group_appointment"):
			events = get_registration_count(self.appointment_type, self.start_dt)
			inconsistency = 0

			corresponding_events = filter(lambda x: get_datetime(x.start_dt) == get_datetime(self.start_dt), events)
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

	def before_save(self):
		if self.start_dt:
			self.start_dt = get_datetime(self.start_dt).replace(tzinfo=None)
		if self.end_dt:
			self.end_dt = get_datetime(self.end_dt).replace(tzinfo=None)

		if self.start_dt and self.end_dt:
			if self.all_day:
				self.end_dt = get_datetime(self.end_dt).replace(hour=23, minute=59, second=59)

			self.duration = (get_datetime(self.end_dt) - get_datetime(self.start_dt)).seconds/60

	def on_update(self):
		self.clear_reminders()

		if self.status == "Confirmed" and self.reminder == 1 and not self.group_event:
			if frappe.db.get_value("Patient Record", self.patient_record, "email_id") != self.email:
				frappe.db.set_value("Patient Record", self.patient_record, "email_id", self.email)

		if self.status == "Confirmed" and self.sms_reminder == 1 and not self.group_event:
			if self.mobile_no is None:
				frappe.throw(_("Please enter a valid mobile number"))
			
			valid_number = validate_receiver_no(self.mobile_no)
			if frappe.db.get_value("Patient Record", self.patient_record, "mobile_no") != valid_number:
				frappe.db.set_value("Patient Record", self.patient_record, "mobile_no", valid_number)

			self.send_sms_reminder(valid_number)

	def on_cancel(self):
		self.clear_reminders()

	def on_trash(self):
		self.clear_reminders()

	def clear_reminders(self):
		sms_reminder = frappe.get_all("SMS Reminder", filters={"maia_appointment": self.name})
		for sms in sms_reminder:
			frappe.delete_doc("SMS Reminder", sms.name, force=True, ignore_permissions=True)

	def send_sms_reminder(self, valid_number):
		appointment_date = formatdate(get_datetime_str(self.start_dt), "dd/MM/yyyy")
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
		
		return {
			"sender_name": sms_settings[0]["sender_name"] or default_sender if sms_settings else default_sender,
			"sms_content": sms_settings[0]["sms_content"] or default_content if sms_settings else default_content,
			"send_before": sms_settings[0]["send_before"] or default_send_before if sms_settings else default_send_before
		}

def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		'no_breadcrumbs': True,
		"title": _("My Appointments"),
		"get_list": get_appointment_list,
		"row_template": "templates/includes/appointments/appointment_row.html"
	}

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

@frappe.whitelist()
def update_status(appointmentId, status):
	frappe.db.set_value("Maia Appointment", appointmentId, "status", status)

@frappe.whitelist()
def get_registration_count(appointment_type, date):
	filters=[
		["Maia Appointment","appointment_type","=",appointment_type],
		["Maia Appointment","group_event","=",1],
		["Maia Appointment", "status","!=", "Cancelled"]
	]
	start = get_datetime(date)
	end = add_to_date(start, years=1)

	_appointment_type = frappe.get_doc("Maia Appointment Type", appointment_type)

	slots = get_events(start=start, end=end, filters=filters)

	for slot in slots:
		filters = [
			["Maia Appointment","appointment_type","=",appointment_type],
			["Maia Appointment","group_event","=",0],
			["Maia Appointment", "status","!=", "Cancelled"]
		]
		scheduled_events = get_events(start=slot.start_dt, end=slot.end_dt, filters=filters)

		count = 0
		registered = []
		if scheduled_events:
			for scheduled_event in scheduled_events:
				count += 1
				registered.append({'name': scheduled_event.name, 'patient': scheduled_event.patient_record})

		slot["already_registered"] = count
		slot["number_of_patients"] = _appointment_type.number_of_patients
		slot["seats_left"] = _appointment_type.number_of_patients - count
		slot["registered"] = registered

	return slots

@frappe.whitelist()
def get_events(start, end, user=None, filters=None):
	if user:
		practitioner = frappe.db.get_value('Professional Information Card', {'user': frappe.session.user}, 'name')
		if practitioner:
			filters = frappe.parse_json(filters) if filters else []
			filters.append(["Maia Appointment","practitioner","=",practitioner])

	from frappe.desk.calendar import get_event_conditions
	add_filters = get_event_conditions("Maia Appointment", filters)

	events = frappe.db.sql("""SELECT
			name, subject, patient_record, appointment_type, practitioner,
			color, start_dt, end_dt, duration, repeat_this_event, repeat_till,
			docstatus, rrule, all_day
		FROM `tabMaia Appointment`
		WHERE
		(
			(
				(date(start_dt) BETWEEN date(%(start)s) AND date(%(end)s))
				OR (date(end_dt) BETWEEN date(%(start)s) AND date(%(end)s))
				OR (
					date(start_dt) <= date(%(start)s)
					AND date(end_dt) >= date(%(end)s)
				)
			)
			OR (
				date(start_dt) <= date(%(start)s)
				AND repeat_this_event=1
				AND coalesce(repeat_till, '3000-01-01') > date(%(start)s)
			)
		)
		AND docstatus < 2
		AND status != "Cancelled" {add_filters}""".format(add_filters=add_filters),
		{
			"start": start,
			"end": end
		}, as_dict=True)

	# process recurring events
	result = list(events)
	for event in events:
		if event.get("repeat_this_event"):
			result = [x for x in result if x.get("name") != event.get("name")]
			result.extend(process_recurring_events(event, start, end, "start_dt", "end_dt", "rrule"))

	return result

@frappe.whitelist()
def check_availability_by_midwife(practitioner, date, duration, appointment_type=None):
	if not (practitioner or date or duration):
		frappe.throw(_("Please select a Midwife, a Date and an Appointment Type"))

	if appointment_type is not None:
		group = frappe.db.get_value("Maia Appointment Type", appointment_type, 'group_appointment')
		if group == 1 :
			return 'group_appointment'
		else:
			return _get_availability_by_midwife(practitioner, date, duration)
	else:
		return _get_availability_by_midwife(practitioner, date, duration)

def _get_availability_by_midwife(practitioner, date, duration):
	payload = {}
	payload[practitioner] = check_availability(practitioner, date, duration)

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
			"tag": frappe.conf.get("customer")+ "/" + sms.sender
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


# Google Calendar
def insert_event_to_calendar(account, event, recurrence=None):
	"""
		Inserts event in Maia Calendar during Sync
	"""
	start = event.get("start")
	end = event.get("end")

	calendar_event = {
		"doctype": "Maia Appointment",
		"subject": event.get("summary"),
		"notes": event.get("description"),
		"sync_with_google_calendar": 1,
		"google_calendar": account.name,
		"google_calendar_id": account.google_calendar_id,
		"google_calendar_event_id": event.get("id"),
		"rrule": recurrence,
		"start_dt": get_datetime(start.get("date")) if start.get("date") else get_timezone_naive_datetime(start),
		"end_dt": get_datetime(end.get("date")) if end.get("date") else get_timezone_naive_datetime(end),
		"all_day": 1 if start.get("date") else 0,
		"repeat_this_event": 1 if recurrence else 0,
		"status": "Confirmed",
		"reminder": 0,
		"sms_reminder": 0,
		"personal_event": 1,
		"practitioner": frappe.db.get_value("Professional Information Card", dict(google_calendar=account.name))
	}
	doc = frappe.get_doc(calendar_event)
	doc.flags.pulled_from_google_calendar = True
	doc.insert(ignore_permissions=True)

def update_event_in_calendar(account, event, recurrence=None):
	"""
		Updates Event in Dokos Calendar if any existing Google Calendar Event is updated
	"""
	start = event.get("start")
	end = event.get("end")

	calendar_event = frappe.get_doc("Maia Appointment", {"google_calendar_event_id": event.get("id")})

	updated_event = {
		"subject": event.get("summary"),
		"notes": event.get("description"),
		"rrule": recurrence,
		"start_dt": get_datetime(start.get("date")) if start.get("date") else get_timezone_naive_datetime(start),
		"end_dt": get_datetime(end.get("date")) if end.get("date") else get_timezone_naive_datetime(end),
		"all_day": 1 if start.get("date") else 0,
		"repeat_this_event": 1 if recurrence else 0,
		"status": "Confirmed",
		"practitioner": calendar_event.practitioner or frappe.db.get_value("Professional Information Card", dict(google_calendar=account.name))
	}

	if calendar_event.personal_event:
		updated_event.update({
			"reminder": 0,
			"sms_reminder": 0,
			"personal_event": 1
		})

	update = False
	for field in updated_event:
		if field == "rrule" and recurrence:
			update = calendar_event.get(field) is None or (set(calendar_event.get(field).split(";")) != set(updated_event.get(field).split(";")))
		else:
			update = (str(calendar_event.get(field)) != str(updated_event.get(field)))
		if update:
			break

	if update:
		calendar_event.update(updated_event)
		calendar_event.flags.pulled_from_google_calendar = True
		calendar_event.save()

def cancel_event_in_calendar(account, event):
	# If any synced Google Calendar Event is cancelled, then close the Event
	add_comment = False

	if frappe.db.exists("Maia Appointment", {"google_calendar_id": account.google_calendar_id, \
		"google_calendar_event_id": event.get("id")}):
		booking = frappe.get_doc("Maia Appointment", {"google_calendar_id": account.google_calendar_id, \
			"google_calendar_event_id": event.get("id")})

		try:
			booking.flags.pulled_from_google_calendar = True
			booking.delete()
			add_comment = False
		except frappe.LinkExistsError:
			# Try to delete event, but only if it has no links
			add_comment = True

	if add_comment:
		frappe.get_doc({
			"doctype": "Comment",
			"comment_type": "Info",
			"reference_doctype": "Maia Appointment",
			"reference_name": booking.get("name"),
			"content": " {0}".format(_("- Event deleted from Google Calendar.")),
		}).insert(ignore_permissions=True)

def insert_event_in_google_calendar(doc, method=None):
	"""
		Insert Events in Google Calendar if sync_with_google_calendar is checked.
	"""
	if not frappe.db.exists("Google Calendar", {"name": doc.google_calendar}) \
		or doc.flags.pulled_from_google_calendar or not doc.sync_with_google_calendar:
		return

	google_calendar, account = get_google_calendar_object(doc.google_calendar)

	if not account.push_to_google_calendar:
		return

	event = {
		"summary": doc.subject,
		"description": doc.notes,
		"recurrence": [doc.rrule] if doc.repeat_this_event and doc.rrule else []
	}
	print(doc.start_dt, doc.end_dt)
	event.update(format_date_according_to_google_calendar(doc.get("all_day", 0), \
		get_datetime(doc.start_dt), get_datetime(doc.end_dt)))

	try:
		event = google_calendar.events().insert(calendarId=doc.google_calendar_id, body=event).execute()
		doc.db_set("google_calendar_event_id", event.get("id"), update_modified=False)
		frappe.publish_realtime('event_synced', {"message": _("Event Synced with Google Calendar.")}, user=frappe.session.user)
	except HttpError as err:
		frappe.throw(_("Google Calendar - Could not insert event in Google Calendar {0}, error code {1}."\
			).format(account.name, err.resp.status))

def update_event_in_google_calendar(doc, method=None):
	"""
		Updates Events in Google Calendar if any existing event is modified in Dokos Calendar
	"""
	# Workaround to avoid triggering update when Event is being inserted since
	# creation and modified are same when inserting doc
	if not frappe.db.exists("Google Calendar", {"name": doc.google_calendar}) or \
		doc.modified == doc.creation or not doc.sync_with_google_calendar or doc.flags.pulled_from_google_calendar:
		return

	if doc.sync_with_google_calendar and not doc.google_calendar_event_id:
		# If sync_with_google_calendar is checked later, then insert the event rather than updating it.
		insert_event_in_google_calendar(doc)
		return

	google_calendar, account = get_google_calendar_object(doc.google_calendar)

	if not account.push_to_google_calendar:
		return

	try:
		event = google_calendar.events().get(calendarId=doc.google_calendar_id, \
			eventId=doc.google_calendar_event_id).execute()
		event["summary"] = doc.subject
		event["description"] = doc.notes
		event["recurrence"] = [doc.rrule] if doc.repeat_this_event and doc.rrule else []
		event["status"] = "cancelled" if doc.status == "Cancelled" else "confirmed"
		print("DATES", doc.start_dt, doc.end_dt)
		event.update(format_date_according_to_google_calendar(doc.get("all_day", 0), \
			get_datetime(doc.start_dt), get_datetime(doc.end_dt)))

		google_calendar.events().update(calendarId=doc.google_calendar_id, \
			eventId=doc.google_calendar_event_id, body=event).execute()
		frappe.publish_realtime('event_synced', {"message": _("Event Synced with Google Calendar.")}, user=frappe.session.user)
	except HttpError as err:
		frappe.throw(_("Google Calendar - Could not update Event {0} in Google Calendar, error code {1}."\
			).format(doc.name, err.resp.status))

def delete_event_in_google_calendar(doc, method=None):
	"""
		Delete Events from Google Calendar if Maia Appointment is deleted.
	"""

	if not frappe.db.exists("Google Calendar", {"name": doc.google_calendar}) or \
		not doc.sync_with_google_calendar or doc.flags.pulled_from_google_calendar:
		return

	google_calendar, account = get_google_calendar_object(doc.google_calendar)

	if not account.push_to_google_calendar:
		return

	try:
		event = google_calendar.events().get(calendarId=doc.google_calendar_id, \
			eventId=doc.google_calendar_event_id).execute()
		event["recurrence"] = None
		event["status"] = "cancelled"

		google_calendar.events().update(calendarId=doc.google_calendar_id, \
			eventId=doc.google_calendar_event_id, body=event).execute()
	except HttpError as err:
		frappe.msgprint(_("Google Calendar - Could not delete Event {0} from Google Calendar, error code {1}."\
			).format(doc.name, err.resp.status))

@frappe.whitelist()
def cancel_appointment(doc):
	frappe.db.set_value("Maia Appointment", doc, "status", "Cancelled")
	appointment = frappe.get_doc("Maia Appointment", doc)
	appointment.flags.ignore_permissions = True
	return appointment.cancel()