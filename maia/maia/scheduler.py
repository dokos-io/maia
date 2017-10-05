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


def check_availability(doctype, df, dt, dn, date, duration):
    date = getdate(date)
    day = calendar.day_name[date.weekday()]
    if date < getdate():
        frappe.throw(_("You cannot schedule for past dates"))

    resource = frappe.get_doc(dt, dn)
    availability = []
    schedules = []

    if hasattr(resource, "consulting_schedule") and resource.consulting_schedule:
        day_sch = filter(lambda x: x.day == day, resource.consulting_schedule)
        if not day_sch:
            availability.append(
                {"msg": _("{0} not available on {1} {2}").format(dn, _(day), formatdate(get_datetime_str(date), "dd/MM/yyyy"))})
            return availability
        for line in day_sch:
            if(datetime.datetime.combine(date, get_time(line.end_time)) > now_datetime()):
                schedules.append({"start": datetime.datetime.combine(date, get_time(line.start_time)), "end": datetime.datetime.combine(
                    date, get_time(line.end_time)), "duration": datetime.timedelta(minutes=cint(duration))})
            if not schedules:
                for sch in day_sch:
                    availability.append({"msg": _(
                        "Schedules for {0} on  {1} : {2}-{3}").format(dn, formatdate(get_datetime_str(date), "dd/MM/yyyy"), sch.start_time, sch.end_time)})
            if schedules:
                availability.extend(get_availability_from_schedule(doctype, df, dn, schedules, date))
    return availability


def get_availability_from_schedule(doctype, df, dn, schedules, date):
    from maia.maia.doctype.midwife_appointment.midwife_appointment import get_events
    data = []
    for line in schedules:
        duration = get_time(line["duration"])
        events = get_events(line["start"].strftime(
            "%Y-%m-%d %H:%M:%S"), line["end"].strftime("%Y-%m-%d %H:%M:%S"), filters=[["Midwife Appointment","practitioner","=",dn]])

        event_list = []
        for event in events:
            if (get_datetime(event.start_dt) >= line["start"] and get_datetime(event.start_dt) <= line["end"]) or get_datetime(event.end_dt) >= line["start"]:
                event_list.append(event)

        available_slot = find_available_slot(date, duration, line, event_list)
        data.append(available_slot)

    return data


def find_available_slot(date, duration, line, scheduled_items):

    available_slots = []
    current_schedule = []
    if scheduled_items:
        for scheduled_item in scheduled_items:

            if get_datetime(scheduled_item.start_dt) < line["start"]:
                new_entry = (get_datetime(line["start"]),
                             get_datetime(scheduled_item.end_dt))
            elif get_datetime(scheduled_item.start_dt) < line["end"]:
                new_entry = (get_datetime(scheduled_item.start_dt),
                         get_datetime(scheduled_item.end_dt))
            try:
                current_schedule.append(new_entry)
            except:
                pass

        scheduled_items = sorted(current_schedule, key = lambda x: x[0])
        final_schedule = list(reduced(scheduled_items))
        slots = get_all_slots(
            line["start"], line["end"], line["duration"], final_schedule)

        for slot in slots:
            available_slots.append(get_dict(slot[0], slot[1]))

        return available_slots

    else:
        slots = get_all_slots(line["start"], line["end"], line["duration"])

        for slot in slots:
            available_slots.append(get_dict(slot[0], slot[1]))

        return available_slots


def get_all_slots(day_start, day_end, time_delta, scheduled_items=None):
    interval = int(time_delta.total_seconds() / 60)

    if scheduled_items:
        slots = sorted([(day_start, day_start)] +
                       scheduled_items + [(day_end, day_end)])
    else:
        slots = sorted([(day_start, day_start)] + [(day_end, day_end)])

    free_slots = []
    for start, end in ((slots[i][1], slots[i + 1][0]) for i in range(len(slots) - 1)):
        while start + timedelta(minutes=interval) <= end:
            free_slots.append([start, start + timedelta(minutes=interval)])
            start += timedelta(minutes=interval)
    return free_slots


def get_dict(start, end, slots=None):
    return {"start": start, "end": end}

def reduced(timeseries):
    prev = datetime.datetime.min
    for start, end in timeseries:
        if end > prev:
            prev = end
            yield start, end
