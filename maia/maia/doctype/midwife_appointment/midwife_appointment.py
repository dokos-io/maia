# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.scheduler import check_availability


class MidwifeAppointment(Document):
	pass


@frappe.whitelist()
def get_events(start, end, filters=None):
        """Returns events for Gantt / Calendar view rendering.
        :param start: Start date-time.
        :param end: End date-time.
        :param filters: Filters (JSON).
        """
        from frappe.desk.calendar import get_event_conditions
        conditions = get_event_conditions("Midwife Appointment", filters)
        data = frappe.db.sql("""select name, patient_record, appointment_type, start_dt, end_dt from `tabMidwife Appointment` where (start_dt between %(start)s and %(end)s) and docstatus < 2 {conditions}""".format(conditions=conditions), {
                "start": start,
                "end": end
        }, as_dict=True, update={"allDay": 0})
        return data

@frappe.whitelist()
def check_availability_by_midwife(practitioner, date, time=None, end_dt=None):
        if not (practitioner or date):
                frappe.throw(_("Please select Physician and Date"))
        payload = {}
        payload[practitioner] = check_availability("Midwife Appointment", "practicioner", False, "Professional Information Card", practitioner, date, time, end_dt)
        return payload
