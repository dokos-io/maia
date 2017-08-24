# Copyright (c) 2017, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, now_datetime, nowtime, cint, get_datetime, add_days
from frappe import _
import datetime
from datetime import timedelta, date
import calendar
from maia.maia.scheduler import get_availability_from_schedule

def get_context(context):
            context.appointment_type = frappe.get_list("Midwife Appointment Type", fields=['name'])
            context.practitioner = frappe.get_list("Professional Information Card", fields=['name'])
                    

def daterange(start_date, end_date):
            if start_date < now_datetime():
                        start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
            for n in range(int ((end_date - start_date).days)):
                        yield start_date + timedelta(n)
                                    
@frappe.whitelist()
def check_availabilities(practitioner, start, end, appointment_type):
            
            duration = frappe.get_value("Midwife Appointment Type", appointment_type, "duration")

            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')
            days_limit = frappe.get_value("Professional Information Card", practitioner, "number_of_days_limit") 
            frappe.logger().debug(days_limit)
            limit = datetime.datetime.combine(add_days(getdate(), int(days_limit)), datetime.datetime.time(datetime.datetime.now()))

            payload = []
            if start < limit:
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
def submit_appointment(patient_record, practitioner, appointment_type, start, end, subject, notes):

            start_date = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').date()
            start_time = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').time()
            app_type = frappe.get_doc("Midwife Appointment Type", appointment_type)
            
            appointment = frappe.get_doc({
                        "doctype": "Midwife Appointment",
                        "patient_record": patient_record,
                        "practitioner": practitioner,
                        "appointment_type": appointment_type,
                        "date": start_date,
                        "start_time": start_time,
                        "start_dt": start,
                        "end_dt": end,
                        "duration": app_type.duration,
                        "color": app_type.color,
                        "subject": subject,
                        "notes": notes
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
