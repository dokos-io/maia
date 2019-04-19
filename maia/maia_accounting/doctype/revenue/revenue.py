# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.accounting_controller import AccountingController

class Revenue(AccountingController):
	def after_insert(self):
		if self.codifications:
			for codification in self.codifications:
				if not codification.description:
					codification.description = frappe.db.get_value("Codification", codification.codification, "codification_description")

	def validate(self):
		if not self.label:
			if self.revenue_type == "Consultation" and self.patient:
				self.label = "{0}-{1}".format(self.patient, _(self.revenue_type))
			elif self.party:
				self.label = "{0}-{1}".format(self.party, _(self.revenue_type))

		self.calculate_totals()
		self.set_status()

	def before_submit(self):
		self.calculate_totals()
		self.set_outstanding_amount()

	def calculate_totals(self):
		self.calculate_line_total()
		self.calculate_total()

	def calculate_line_total(self):
		if self.with_items:
			for codification in self.codifications:
				codification.total_amount = float(codification.qty) * float(codification.unit_price)

	def calculate_total(self):
		if self.with_items:
			total = 0
			for codification in self.codifications:
				total += codification.total_amount

			self.amount = total

@frappe.whitelist()
def get_asset_revenue(dt, dn):
	asset = frappe.get_doc(dt, dn)

	revenue = frappe.new_doc("Revenue")
	revenue.label = asset.asset_label
	revenue.revenue_type = "Miscellaneous"
	revenue.amount = asset.asset_value
	revenue.accounting_item = frappe.db.get_value("Accounting Item", dict(accounting_item_type="Asset Selling"), "name")

	return revenue