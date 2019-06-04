# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from maia.setup.setup_wizard.operations.dashboard_setup import setup_charts, setup_cards, init_dashboard
from frappe.desk.doctype.desk.desk import create_user_desk

def execute():
	"""
	frappe.reload_doc("desk", "doctype", "dashboard_chart")
	frappe.reload_doc("desk", "doctype", "dashboard_card")
	frappe.reload_doc("desk", "doctype", "dashboard_chart_source")
	frappe.reload_doc("desk", "doctype", "dashboard_card_source")
	frappe.reload_doc("desk", "doctype", "desk")
	frappe.reload_doc("desk", "doctype", "desk_items")
	frappe.reload_doc("desk", "doctype", "dashboard_calendar")
	"""

	frappe.model.sync.sync_all()

	for user in frappe.get_all("User", filters={"user_type": "System User"}):
		create_user_desk(user.name)

	setup_charts()
	setup_cards()
	init_dashboard()