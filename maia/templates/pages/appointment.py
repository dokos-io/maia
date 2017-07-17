# Copyright (c) 2017, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe

def get_context(context):
    context.appointment_type = frappe.get_list("Midwife Appointment Type", fields=['name']) 
    context.practitioner = frappe.get_list("Professional Information Card", fields=['name']) 
