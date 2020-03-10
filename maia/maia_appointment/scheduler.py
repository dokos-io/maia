# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# Original Code by ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint, get_datetime, formatdate, get_datetime_str
from frappe import _
import datetime
from datetime import timedelta
import calendar

def check_availability(practitioner, date, duration):
	date = getdate(date)
	day = calendar.day_name[date.weekday()]
	if date < getdate():
		frappe.throw(_("You cannot schedule for past dates"))

	professional_informations = frappe.get_doc("Professional Information Card", practitioner)

	availability = []
	schedules = []

	if getattr(professional_informations, "consulting_schedule"):
		day_schedule = list(filter(lambda x: x.day == day, professional_informations.consulting_schedule))
		if not day_schedule:
			availability.append({"msg": _("{0} not available on {1} {2}").format(practitioner, _(day), \
				formatdate(get_datetime_str(date), "dd/MM/yyyy"))})
			return availability

		for line in day_schedule:
			if(datetime.datetime.combine(date, get_time(line.end_time)) > now_datetime()):
				schedules.append({
					"start": datetime.datetime.combine(date, get_time(line.start_time)),
					"end": datetime.datetime.combine(date, get_time(line.end_time)),
					"duration": datetime.timedelta(minutes=cint(duration))
				})

		if schedules:
			schedule_availability = ScheduleAvailability(practitioner, schedules, date)
			availability.extend(schedule_availability.get_availabilities())

		if not schedules and not availability:
			for line in day_schedule:
				availability.append({"msg": _("Schedules for {0} on  {1} : {2}-{3}").format(\
					practitioner, formatdate(get_datetime_str(date), "dd/MM/yyyy"), line.start_time, line.end_time)})

	return availability

class ScheduleAvailability():
	def __init__(self, docname, schedules, date):
		self.docname = docname
		self.schedules = schedules
		self.date = date

	def get_availabilities(self):
		from maia.maia_appointment.doctype.maia_appointment.maia_appointment import get_events
		data = []
		for line in self.schedules:
			duration = get_time(line["duration"])
			events = get_events(
				line["start"].strftime("%Y-%m-%d %H:%M:%S"),
				line["end"].strftime("%Y-%m-%d %H:%M:%S"),
				filters=[["Maia Appointment","practitioner","=",self.docname]]
			)

			event_list = []
			for event in events:
				if (get_datetime(event.get("start_dt")) >= line["start"] and get_datetime(event.get("start_dt")) <= line["end"]) \
					or get_datetime(event.get("end_dt")) >= line["start"]:
					event_list.append(event)

			available_slot = self.find_available_slot(duration, line, event_list)
			data.extend(available_slot)

		return data

	def find_available_slot(self, duration, line, scheduled_items):
		available_slots = []
		current_schedule = []
		if scheduled_items:
			for scheduled_item in scheduled_items:
				if get_datetime(scheduled_item.get("start_dt")) > get_datetime(scheduled_item.get("end_dt")):
					continue
				elif get_datetime(scheduled_item.get("start_dt")) < line["start"]:
					new_entry = (get_datetime(line["start"]), get_datetime(scheduled_item.get("end_dt")))
				elif get_datetime(scheduled_item.get("start_dt")) < line["end"]:
					new_entry = (get_datetime(scheduled_item.get("start_dt")), get_datetime(scheduled_item.get("end_dt")))

				try:
					current_schedule.append(new_entry)
				except Exception as e:
					print(e)

			scheduled_items = sorted(current_schedule, key = lambda x: x[0])
			final_schedule = list(reduced(scheduled_items))
			slots = self.get_all_slots(line["start"], line["end"], line["duration"], final_schedule)

			for slot in slots:
				available_slots.append({"start": slot[0], "end": slot[1]})

		else:
			slots = self.get_all_slots(line["start"], line["end"], line["duration"])

			for slot in slots:
				available_slots.append({"start": slot[0], "end": slot[1]})

		return available_slots

	def get_all_slots(self, day_start, day_end, time_delta, scheduled_items=None):
		interval = int(time_delta.total_seconds() / 60)

		if scheduled_items:
			slots = sorted([(day_start, day_start)] + scheduled_items + [(day_end, day_end)])
		else:
			slots = sorted([(day_start, day_start)] + [(day_end, day_end)])

		free_slots = []
		for start, end in ((slots[i][1], slots[i + 1][0]) for i in range(len(slots) - 1)):
			while start + timedelta(minutes=interval) <= end:
				free_slots.append([start, start + timedelta(minutes=interval)])
				start += timedelta(minutes=interval)
		return free_slots

def reduced(timeseries):
	prev = datetime.datetime.min
	for start, end in timeseries:
		if end > prev:
			prev = end
			yield start, end
