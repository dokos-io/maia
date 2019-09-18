# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# License: See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	cards = frappe.get_all("Dashboard Card", fields=["name", "card_type"])
	charts = frappe.get_all("Dashboard Chart", fields=["name", "chart_type"])

	for card in cards:
		if card["card_type"] == "Preregistered":
			frappe.db.set_value("Dashboard Card", card["name"], "card_type", "Custom")

	for chart in charts:
		if chart["chart_type"] == "Preregistered":
			frappe.db.set_value("Dashboard Chart", chart["name"], "chart_type", "Custom")
