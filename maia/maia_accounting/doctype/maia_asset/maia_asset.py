# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.status_updater import StatusUpdater
from frappe.utils import getdate, add_months, date_diff, add_days, flt, nowdate
from pandas.tseries import offsets
import json
import os

class MaiaAsset(StatusUpdater):
	def validate(self):
		self.set_status()

	def is_fully_depreciated(self):
		if len(self.past_depreciations()) < len(self.asset_depreciations):
			return 0
		else:
			return 1

	def is_party_depreciated(self):
		if len(self.past_depreciations()) < len(self.asset_depreciations) and len(self.past_depreciations()) > 0:
			return 1
		else:
			return 0

	def is_not_depreciated(self):
		if not self.past_depreciations():
			return 1
		else: return 0

	def past_depreciations(self):
		return frappe.get_all("Maia Asset Depreciation", filters={"parent": self.name, "parenttype": self.doctype, "depreciation_document": ["!=", None]})

@frappe.whitelist()
def get_depreciation_schedule(doc):
	doc = json.loads(doc)
	next_depreciation_date = getdate(doc["acquisition_date"])
	rate = doc["depreciation_rate"]
	depreciation_base = doc["asset_value"]
	cumulated_depreciation = 0

	depreciation_entries = []

	for n in range(int(doc["depreciation_duration"]) + 1):
		previous_depreciation_date = next_depreciation_date

		if n == 0:
			next_depreciation_date = getdate(previous_depreciation_date + offsets.YearEnd())
			days_diff = date_diff(next_depreciation_date, previous_depreciation_date)

		elif n == int(doc["depreciation_duration"]):
			next_depreciation_date = add_days(previous_depreciation_date, (360 - days_diff))

		else:
			next_depreciation_date = add_months(previous_depreciation_date, 12)

		depreciation_amount = get_depreciation_amount(
			previous_date=previous_depreciation_date,
			next_date=next_depreciation_date,
			doc=doc)

		max_deductible = depreciation_amount
		if doc["deduction_ceiling"] > 0:
			max_deductible = get_deductible_amount(
				previous_date=previous_depreciation_date,
				next_date=next_depreciation_date,
				doc=doc)

		cumulated_depreciation += flt(depreciation_amount)

		depreciation_entries.append({
			"depreciation_date": next_depreciation_date,
			"depreciation_base": depreciation_base,
			"depreciation_amount": depreciation_amount,
			"max_deductible": max_deductible,
			"cumulated_depreciation": cumulated_depreciation
		})
		
		depreciation_base -= flt(depreciation_amount)

		if cumulated_depreciation >= doc["asset_value"]:
			break
	
	return depreciation_entries

def get_prorata_ratio(previous_date, next_date):
	return min(abs(flt(date_diff(str(next_date), str(previous_date)))/360), 1)

def get_depreciation_amount(**kwargs):
	return (kwargs["doc"]["depreciation_rate"] / 100) * kwargs["doc"]["asset_value"] \
		* get_prorata_ratio(kwargs["previous_date"], kwargs["next_date"])

def get_deductible_amount(**kwargs):
	return (kwargs["doc"]["depreciation_rate"] / 100) * kwargs["doc"]["deduction_ceiling"] \
		* get_prorata_ratio(kwargs["previous_date"], kwargs["next_date"])

@frappe.whitelist()
def get_deduction_ceiling(year, co2_rate):
	path = os.path.join(frappe.get_module_path('maia_accounting'), "doctype", "maia_asset", "car_deduction_ceiling_fr.json") 
	data = frappe.get_file_json(path)

	if getdate(year).year in data:
		year_data = data[getdate(year).year]
	else:
		year_data = data[next(iter(data))]

	for d in year_data:
		if flt(co2_rate) <= flt(d):
			return year_data[d]

def post_depreciations():
	for asset in frappe.get_all("Maia Asset", filters={"docstatus": 1}):
		doc = frappe.get_doc("Maia Asset", asset.name)

		depreciation_account = frappe.get_doc("Accounting Item", dict(accounting_item_type="Asset depreciation"))
		deductible_account = frappe.get_doc("Accounting Item", dict(accounting_item_type="Asset depreciation charge"))
		non_deductible_account = frappe.get_doc("Accounting Item", dict(accounting_item_type="Practitioner"))

		for depreciation in doc.asset_depreciations:
			if getdate(depreciation.depreciation_date) <= getdate(nowdate()) and not depreciation.depreciation_document:
				new_depreciation = frappe.new_doc("Miscellaneous Operation")
				new_depreciation.posting_date = depreciation.depreciation_date
				new_depreciation.practitioner = doc.practitioner
				new_depreciation.append("items", {
					'accounting_item': depreciation_account.name,
					'amount': -depreciation.depreciation_amount
				})
				new_depreciation.append("items", {
					'accounting_item': deductible_account.name,
					'amount': depreciation.deductible_amount
				})

				if flt(depreciation.non_deductible_amount) > 0:
					new_depreciation.append("items", {
						'accounting_item': non_deductible_account.name,
						'amount': depreciation.non_deductible_amount
					})
				
				new_depreciation.insert(ignore_permissions=True)
				new_depreciation.submit()

				frappe.db.set_value("Maia Asset Depreciation", depreciation.name, "depreciation_document", new_depreciation.name)

		doc.set_status()

