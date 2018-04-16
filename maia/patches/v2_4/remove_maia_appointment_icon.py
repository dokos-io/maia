# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.sql('Delete from `tabDesktop Icon` where label="Midwife Appointment"')
