# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import os
from frappe import _
from frappe.utils import update_progress_bar
from maia.maia_accounting.doctype.maia_asset.maia_asset import post_depreciations

def execute():
	assets = frappe.get_all("Asset", dict(docstatus=1))

	l = len(assets)

	for i, a in enumerate(assets):
		asset = frappe.get_doc("Asset", a.name)
		
		new_asset = frappe.new_doc("Maia Asset")
		new_asset.asset_type = "General"
		new_asset.asset_label = asset.asset_name
		new_asset.practitioner = frappe.db.get_value("Professional Information Card", dict(company=asset.company), "name")
		new_asset.acquisition_date = asset.purchase_date
		new_asset.asset_value = asset.gross_purchase_amount
		new_asset.professional_percentage = 100

		depreciations = []
		base = asset.gross_purchase_amount
		for dep in asset.schedules:
			planned_dep = {
				"depreciation_date": dep.schedule_date,
				"depreciation_amount": dep.depreciation_amount,
				"cumulated_depreciation": dep.accumulated_depreciation_amount,
				"depreciation_base": base,
				"deductible_amount": dep.depreciation_amount,
				"non_deductible_amount": 0
			}

			base -= dep.depreciation_amount

			new_asset.append("asset_depreciations", planned_dep)

		new_asset.insert(ignore_permissions=True)
		new_asset.submit()

		update_progress_bar("Migrating Assets", i, l)

	frappe.db.commit()

	post_depreciations()
