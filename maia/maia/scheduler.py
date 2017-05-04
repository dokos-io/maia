# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# Original Code by ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint
from frappe import msgprint, _
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
                msg = ""
                for sch in day_sch:
                    msg += " <br>{0}-{1}".format(sch.start_time, sch.end_time)
                    availability.append({"msg": _("Schedules for {0} on  {1} :  {2} ").format(dn, date, msg)})
            if schedules:
                availability.extend(get_availability_from_schedule(doctype, df, dn, schedules, date))            
    return availability

def get_availability_from_schedule(doctype, df, dn, schedules, date):
    data = []
    for line in schedules:
        duration = get_time(line["duration"])
        scheduled_items = frappe.db.sql("""select start_dt, duration from `tab{0}` where (docstatus=0 or docstatus=1) and {1}='{2}' and start_dt between '{3}' and '{4}' order by start_dt""".format(doctype, df, dn, line["start"], line["end"]))

        
        #A session in progress - return slot > current time
        if(line["start"] < now_datetime()):
            time = now_datetime()
            data.append(find_available_slot(date, duration, line, scheduled_items, time))
            continue
        
        data.append(find_available_slot(date, duration, line, scheduled_items))
    return data

def find_available_slot(date, duration, line, scheduled_items, time=None):
    slots = get_all_slots(line["start"], line["end"], line["duration"], time)
    available_slots = []
    current_schedule = []
    if scheduled_items:
        for scheduled_item in scheduled_items:
            current_schedule.append(scheduled_item)

            dur = get_time(scheduled_item[1])
            item_end = scheduled_item[0] + datetime.timedelta(hours = dur.hour, minutes=dur.minute)

            new_item = datetime.datetime.now()
            while (new_item <= item_end):
                new_item = scheduled_item[0] + datetime.timedelta(hours = duration.hour, minutes=duration.minute)
                new_entry = (new_item, scheduled_item[1])
                current_schedule.append(new_entry)

        scheduled_items = tuple(current_schedule)
        frappe.logger().debug(scheduled_items)    
        scheduled_map = set(map(lambda x : x[0], scheduled_items))
        slots_free = [x for x in slots if x not in scheduled_map]
        if not slots_free:
            return {"msg": _("No slots left for schedule {0} {1}").format(line["start"], line["end"])}

        for slot_free in slots_free:
            end = slot_free + datetime.timedelta(hours = duration.hour, minutes=duration.minute)
            available_slots.append(get_dict(slot_free, end, slots))

        return available_slots

    else:
        for slot in slots:
            end = slot + datetime.timedelta(hours = duration.hour, minutes=duration.minute)
            available_slots.append(get_dict(slot, end, slots))

        return available_slots

def get_all_slots(start, end, time_delta, time=None):
    interval = int(time_delta.total_seconds() / 60)
    slots = []
    if time:
        start = roundTime(time)
    while start < end:
        slots.append(start)
        start += timedelta(minutes=interval)
    return slots

def get_dict(start, end, slots=None):
    return {"start": start, "end": end}

def roundTime(dt, dateDelta=datetime.timedelta(minutes=5)):
    roundTo = dateDelta.total_seconds()
    seconds = (dt - dt.min).seconds            
    rounding = (seconds+roundTo/2) // roundTo * roundTo

    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)
