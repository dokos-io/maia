# Copyright (c) 2017, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint, get_datetime
from frappe import _
import datetime
from datetime import timedelta, date
import calendar

def get_context(context):
            context.appointment_type = frappe.get_list("Midwife Appointment Type", fields=['name'])
            context.practitioner = frappe.get_list("Professional Information Card", fields=['name'])
                    

def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days)):
                        yield start_date + timedelta(n)
                                    
@frappe.whitelist()
def check_availabilities(practitioner, start, end, appointment_type):
            
            duration = frappe.get_value("Midwife Appointment Type", appointment_type, "duration")

            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')

            payload = []
            for dt in daterange(start, end):
                        date = dt.strftime("%Y-%m-%d")

                        calendar_availability = check_availability("Midwife Appointment", "practitioner", "Professional Information Card", practitioner, date, duration)
                        if bool(calendar_availability) == True:
                                    payload += calendar_availability

            avail = []
            for items in payload:
                        avail += items 

            final_avail = []
            final_avail.append(avail)
            return final_avail

@frappe.whitelist()
def submit_appointment(patient_record, practitioner, appointment_type, start, end):

            start_date = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').date()
            start_time = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').time()
            duration = frappe.get_value("Midwife Appointment Type", appointment_type, "duration")
            
            appointment = frappe.get_doc({
                        "doctype": "Midwife Appointment",
                        "patient_record": patient_record,
                        "practitioner": practitioner,
                        "appointment_type": appointment_type,
                        "date": start_date,
                        "start_time": start_time,
                        "start_dt": start,
                        "end_dt": end,
                        "duration": duration
            }).insert()

            appointment.submit()


def check_availability(doctype, df, dt, dn, date, duration):
    date = getdate(date)
    day = calendar.day_name[date.weekday()]
    if date < getdate():
        pass

    resource = frappe.get_doc(dt, dn)
    availability = []
    schedules = []
    
    if hasattr(resource, "consulting_schedule") and resource.consulting_schedule:
        day_sch = filter(lambda x : x.day == day, resource.consulting_schedule)
        if not day_sch:
            return availability

        for line in day_sch:
            if(datetime.datetime.combine(date, get_time(line.end_time)) > now_datetime()):
                schedules.append({"start": datetime.datetime.combine(date, get_time(line.start_time)), "end": datetime.datetime.combine(date, get_time(line.end_time)), "duration": datetime.timedelta(minutes = cint(duration))})
            
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

def get_dict(start, end):
    return {"start": start, "end": end, "all_day": 0, "id": start}

def roundTime(dt, dateDelta=datetime.timedelta(minutes=5)):
    roundTo = dateDelta.total_seconds()
    seconds = (dt - dt.min).seconds            
    rounding = (seconds+roundTo/2) // roundTo * roundTo

    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)
