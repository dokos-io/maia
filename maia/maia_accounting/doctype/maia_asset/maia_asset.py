# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, date_diff, add_days, flt
from pandas.tseries import offsets
import json

class MaiaAsset(Document):
	pass

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
		cumulated_depreciation += flt(depreciation_amount)

		depreciation_entries.append({
			"depreciation_date": next_depreciation_date,
			"depreciation_base": depreciation_base,
			"depreciation_amount": depreciation_amount,
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