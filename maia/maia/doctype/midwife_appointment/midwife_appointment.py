# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.scheduler import check_availability
import datetime
from frappe.utils import getdate

class MidwifeAppointment(Document):
        pass

@frappe.whitelist()
def update_status(appointmentId, status):
        frappe.db.set_value("Midwife Appointment",appointmentId,"status",status)
       
@frappe.whitelist()
def get_events(start, end, filters=None):
        from frappe.desk.calendar import get_event_conditions
        conditions = get_event_conditions("Midwife Appointment", filters)
        data = frappe.db.sql("""select name, patient_record, appointment_type, start_dt, end_dt from `tabMidwife Appointment` where (start_dt between %(start)s and %(end)s) and docstatus < 2 {conditions}""".format(conditions=conditions), {
                "start": start,
                "end": end
        }, as_dict=True, update={"allDay": 0})
        return data

@frappe.whitelist()
def check_availability_by_midwife(practitioner, date, duration):
        if not (practitioner or date or duration):
                frappe.throw(_("Please select a Midwife, a Date and an Appointment Type"))
        payload = {}
        payload[practitioner] = check_availability("Midwife Appointment", "practitioner", "Professional Information Card", practitioner, date, duration)
        return payload
