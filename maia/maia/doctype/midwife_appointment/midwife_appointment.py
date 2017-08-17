# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.scheduler import check_availability
from dateutil.relativedelta import relativedelta
from frappe import _
import datetime
from frappe.utils import getdate, get_time, get_datetime, get_datetime_str, formatdate, now_datetime, add_days, nowdate
from frappe.email.doctype.standard_reply.standard_reply import get_standard_reply
from mailin import Mailin

class MidwifeAppointment(Document):
        def on_submit(self):
                date = getdate(self.date)
                time = get_time(self.start_time)
                st_dt = datetime.datetime.combine(date, time)
                ed_dt = st_dt + datetime.timedelta(minutes = int(self.duration))
                frappe.db.set_value("Midwife Appointment", self.name, "start_dt", st_dt)
                frappe.db.set_value("Midwife Appointment", self.name, "end_dt", ed_dt)
                self.reload()

                if self.reminder == 1:
                        frappe.db.set_value("Patient Record",self.patient_record,"email_id",self.email)
                        self.send_reminder()

                if self.sms_reminder == 1:
                        number = self.mobile_no
                        valid_number = validate_receiver_no(number)

                        frappe.db.set_value("Patient Record",self.patient_record,"mobile_no",self.mobile_no)

                        self.send_sms_reminder(valid_number)

        def send_reminder(self):
                patient_email = self.email
                sending_date = get_datetime(self.date) + relativedelta(days=-1)

                if self.standard_reply:
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
                        appointment_date = formatdate(getdate(self.date), "dd/MM/yyyy")
                        start_time = get_datetime(self.start_dt).strftime("%H:%M")
                
                        subject = _("""N'oubliez pas votre rendez-vous avec {0}, prévu le {1} à {2}""".format(self.practitioner, appointment_date, start_time))
                        message = _("""Bonjour {0}, <br><br>Votre rendez-vous est toujours prévu le {1}, à {2}. <br><br>Si vous avez un empêchement, veuillez me l'indiquer au plus vite par retour de mail.<br><br>Merci beaucoup.<br><br>{3}""".format(patient_first_name, appointment_date, start_time, self.practitioner))

                if sending_date > now_datetime():
                        frappe.sendmail(patient_email, subject=subject, content=message, send_after=sending_date)
                        self.get_email_id(patient_email, sending_date)
                else:
                        frappe.sendmail(patient_email, subject=subject, content=message)

        def get_email_id(self, patient_email, sending_date):
                email_queue = frappe.get_all("Email Queue")
                queue_id = email_queue[0].name
                frappe.db.set_value("Midwife Appointment",self.name,"queue_id",queue_id)

        def send_sms_reminder(self, valid_number):
                send_after_day = get_datetime(self.start_dt) + relativedelta(days=-1)
                appointment_date = formatdate(getdate(self.date), "dd/MM/yyyy")
                start_time = get_datetime(self.start_dt).strftime("%H:%M")

                sr = frappe.new_doc('SMS Reminder')
                sr.sender_name = "SageFemme"
                sr.sender = self.practitioner
                sr.send_on = send_after_day
                sr.message = _("""Rappel: Vous avez rendez-vous avec {0} le {1} à {2}. En cas d'empêchement, merci de contacter votre sage-femme au plus vite.""".format(self.practitioner, appointment_date, start_time))
                sr.send_to = valid_number
                sr.flags.ignore_permissions = True
                sr.save()
                
        def on_cancel(self):
                queue_name = frappe.db.get_value("Midwife Appointment", self.name, "queue_id")
                if frappe.db.exists("Email Queue", queue_name):
                        frappe.delete_doc("Email Queue", queue_name)
                frappe.db.set_value("Midwife Appointment", self.name, "queue_id", "")

@frappe.whitelist()
def update_status(appointmentId, status):
        frappe.db.set_value("Midwife Appointment",appointmentId,"status",status)
       
@frappe.whitelist()
def get_events(start, end, filters=None):
        from frappe.desk.calendar import get_event_conditions
        conditions = get_event_conditions("Midwife Appointment", filters)
        data = frappe.db.sql("""select name, subject, patient_record, appointment_type, color, start_dt, end_dt from `tabMidwife Appointment` where (start_dt between %(start)s and %(end)s) and docstatus < 2 {conditions}""".format(conditions=conditions), {
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

def validate_receiver_no(validated_no):
                
        for x in [' ', '-', '(', ')', '.']:
                validated_no = validated_no.replace(x, '')
        for y in ['+']:
                validated_no = validated_no.replace(y, '00')

        if not validated_no:
                throw(_("Please enter a valid mobile nunber"))

        return validated_no

def flush(from_test=False):
        """flush email queue, every time: called from scheduler"""
        # additional check
        cache = frappe.cache()
        
        auto_commit = not from_test

        make_cache_queue()

        for i in range(cache.llen('cache_sms_queue')):
                sms = cache.lpop('cache_sms_queue')

                if sms:
                        send_sms_reminder(sms)

def make_cache_queue():
        '''cache values in queue before sendign'''
        cache = frappe.cache()

        sms = frappe.db.sql('''select
        name
        from `tabSMS Reminder`
        where send_on < %(now)s
        order by creation asc
        limit 500''', { 'now': now_datetime() })

        # reset value
        cache.delete_value('cache_sms_queue')
        for e in sms:
                cache.rpush('cache_sms_queue', e[0])

                
def send_sms_reminder(name):
        sms = frappe.db.sql('''select
        name, sender_name, sender, send_on, message, send_to
        from
        `tabSMS Reminder`
        where
        name=%s
        for update''', name, as_dict=True)[0]

        args = {"text": sms.message}
        args["from"] = sms.sender_name
        args["to"] = sms.send_to
        args["type"] = "transactional"
        args["tag"] = sms.sender

        status = send_request( args)

        if status["code"]=="success":
                create_sms_log(args)
                reminder = frappe.get_doc('SMS Reminder', sms.name)
                reminder.delete()

def send_request(params):
        
        m = Mailin("https://api.sendinblue.com/v2.0","jrD175KhgNQcE8U9")
        data = params
        frappe.logger().debug(data)
        result = m.send_sms(data)
        return result

def create_sms_log(args):
        sl = frappe.new_doc('SMS Log')
        sl.sender_name = args['from']
        sl.sent_on = nowdate()
        sl.message = args['text']
        sl.no_of_requested_sms = 1
        sl.requested_numbers = "\n".join(args['to'])
        sl.no_of_sent_sms = 1
        sl.sent_to = "\n".join(args['to'])
        sl.flags.ignore_permissions = True
        sl.save()
