# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# Original Code by ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint
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
        day_sch = filter(lambda x : x.day == day, resource.consulting_schedule)
        if not day_sch:
            availability.append({"msg": _("{0} not available on {1} {2}").format(dn, day, date)})
            return availability
        for line in day_sch:
            if(datetime.datetime.combine(date, get_time(line.end_time)) > now_datetime()):
                schedules.append({"start": datetime.datetime.combine(date, get_time(line.start_time)), "end": datetime.datetime.combine(date, get_time(line.end_time)), "duration": datetime.timedelta(minutes = cint(duration))})
            if not schedules:
                for sch in day_sch:
                    availability.append({"msg": _("Schedules for {0} on  {1} : {2}-{3}").format(dn, date, sch.start_time, sch.end_time)})
            if schedules:
                availability.extend(get_availability_from_schedule(doctype, df, dn, schedules, date))            
    return availability

def get_availability_from_schedule(doctype, df, dn, schedules, date):
    data = []
    for line in schedules:
        duration = get_time(line["duration"])
        scheduled_items = frappe.db.sql("""select start_dt, duration from `tab{0}` where (docstatus=0 or docstatus=1) and {1}='{2}' and start_dt between '{3}' and '{4}' order by start_dt""".format(doctype, df, dn, line["start"], line["end"]))

        available_slot = find_available_slot(date, duration, line, scheduled_items)
        data.append(available_slot)
        
    return data

def find_available_slot(date, duration, line, scheduled_items):
    
    available_slots = []
    current_schedule = []
    if scheduled_items:
        for scheduled_item in scheduled_items:

            dur = datetime.timedelta(minutes = cint(scheduled_item[1]))
            item_end = scheduled_item[0] + dur 
            new_entry = (scheduled_item[0], item_end)
            current_schedule.append(new_entry)

        scheduled_items = current_schedule
        slots = get_all_slots(line["start"], line["end"], line["duration"], scheduled_items)
        
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
                slots = sorted([(day_start, day_start)] + scheduled_items + [(day_end, day_end)])
    else:
                slots = sorted([(day_start, day_start)] + [(day_end, day_end)])

    free_slots = []
    for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):
            while start + timedelta(minutes=interval) <= end:
                        free_slots.append([start, start + timedelta(minutes=interval)])
                        start += timedelta(minutes=interval)
    return free_slots

def get_dict(start, end, slots=None):
    return {"start": start, "end": end}
