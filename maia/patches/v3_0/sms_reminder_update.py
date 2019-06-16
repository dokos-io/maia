# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	sms_queue = frappe.get_all("SMS Reminder", filters={"status": ["in", ["Queued", "Error"]]})

	for sms in sms_queue:
		frappe.db.set_value("SMS Reminder", sms.name, "sender_name", "SageFemme")