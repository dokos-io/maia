# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.scheduler import check_availability
import datetime
import time
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import getdate, get_datetime, get_datetime_str, formatdate, now_datetime
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.email.doctype.standard_reply.standard_reply import get_standard_reply

class MidwifeAppointment(Document):       
        def on_submit(self):
                if self.reminder == 1:
                        frappe.db.set_value("Patient Record",self.patient_record,"email_id",self.email)
                        self.send_reminder()

        def send_reminder(self):
                patient_email = self.email
                sending_date = get_datetime(self.date) + relativedelta(days=-1)

                if self.standard_reply != None:
                        args = {
                                "patient_record": self.patient_record,
                                "patient_first_name": frappe.db.get_value("Patient Record",self.patient_record,"patient_first_name"),
                                "patient_last_name": frappe.db.get_value("Patient Record",self.patient_record,"patient_last_name"),
                                "practitioner": self.practitioner,
                                "appointment_type": self.appointment_type,
                                "patient_name": self.patient_name,
                                "date": formatdate(get_datetime_str(self.start_dt), "dd/MM/yyyy"),
                                "start_time": get_datetime(self.start_dt).strftime("%H:%M"),
                                "standard_reply": self.standard_reply,
                                "duration": self.duration
                        }
                        reply = get_standard_reply(self.standard_reply, args)
                        
                        subject = reply["subject"]
                        message = reply["message"]
                else:
                        patient_first_name = frappe.db.get_value("Patient Record",self.patient_record,"patient_first_name")
                        appointment_date = formatdate(get_datetime_str(self.start_dt), "dd/MM/yyyy")
                        start_time = get_datetime(self.start_dt).strftime("%H:%M")
                
                        subject = _("""N'oubliez pas votre rendez-vous avec {0}, prévu le {1} à {2}""".format(self.practitioner, appointment_date, start_time))
                        message = _("""Bonjour {0}, <br><br>Votre rendez-vous est toujours prévu le {1}, à {2}. <br><br>Si vous avez un empêchement, veuillez me l'indiquer au plus vite par retour de mail.<br><br>Merci beaucoup.<br><br>{3}""".format(patient_first_name, appointment_date, start_time, self.practitioner))

                if sending_date > now_datetime():
                        frappe.sendmail(patient_email, subject=subject, content=message, send_after=sending_date)
                else:
                        frappe.sendmail(patient_email, subject=subject, content=message)

@frappe.whitelist()
def update_status(appointmentId, status):
        frappe.db.set_value("Midwife Appointment",appointmentId,"status",status)
       
@frappe.whitelist()
def get_events(start, end, filters=None):
        from frappe.desk.calendar import get_event_conditions
        conditions = get_event_conditions("Midwife Appointment", filters)
        data = frappe.db.sql("""select name, patient_record, appointment_type, color, start_dt, end_dt from `tabMidwife Appointment` where (start_dt between %(start)s and %(end)s) and docstatus < 2 {conditions}""".format(conditions=conditions), {
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
