# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from maia.setup.setup_wizard.operations.dashboard_setup import setup_card, setup_chart

def execute():
	frappe.model.sync.sync_all()
	frappe.clear_cache()
	card_sources = [frappe._dict({"name": "Outstanding reconciliations"}), frappe._dict({"name": "Patient outstanding amount"}),\
		frappe._dict({"name": "Social security outstanding amount"})]

	for source in card_sources:
		setup_card(source)

	chart_sources = [frappe._dict({"name": "Total consultations per week"}), frappe._dict({"name": "Codifications repartition"})]

	for source in chart_sources:
		setup_chart(source)


	# Correction for existing chart
	frappe.db.set_value("Dashboard Chart", "Répartition des consultations", "unit", "Consultations")
	frappe.db.set_value("Dashboard Chart", "Répartition des consultations", "timeseries", 0)