# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	frappe.rename_doc('DocType', 'Midwife Appointment', 'Maia Appointment')
	frappe.rename_doc('DocType', 'Midwife Appointment Type', 'Maia Appointment Type')
