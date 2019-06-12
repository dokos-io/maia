# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from maia.setup.setup_wizard.operations.dashboard_setup import setup_charts, setup_cards, init_dashboard
from frappe.desk.doctype.desk.desk import create_user_desk

def execute():
	frappe.model.sync.sync_all()
	frappe.clear_cache()

	for user in frappe.get_all("User", filters={"user_type": "System User"}):
		frappe.set_user(user.name)
		create_user_desk(user.name)

	frappe.set_user("Administrator")
	setup_charts()
	setup_cards()
	init_dashboard()