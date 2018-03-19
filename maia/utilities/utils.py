# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now_datetime

def delete_expired_sms():
	data = frappe.get_all("SMS Reminder", fields=["name", "send_on"])

	for d in data:
		if d.send_on < now_datetime():
			frappe.delete_doc("SMS Reminder", d.name, ignore_permissions=True)
