# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from maia.maia_accounting.controllers.accounting_controller import AccountingController
from maia.maia_accounting.utils import get_accounting_query_conditions

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
		self.alert_on_amount()
		self.calculate_totals()
		self.set_outstanding_amount()

	def alert_on_amount(self):
		if not self.amount > 0:
			frappe.throw(_("Please enter an amount > 0"))

	def calculate_totals(self):
		self.calculate_line_total()
		self.calculate_total()

	def calculate_line_total(self):
		if self.with_items:
			for codification in self.codifications:
				if not codification.unit_price:
					frappe.db.set_value("Revenue Items", codification.name, "unit_price", frappe.db.get_value("Codification", codification.codification, "billing_price") or 0)
				if not codification.accounting_item:
					frappe.db.set_value("Revenue Items", codification.name, "accounting_item", frappe.db.get_value("Codification", codification.codification, "accounting_item"))

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

@frappe.whitelist()
def get_billing_address(party_type, party):
	party_links = [x["parent"] for x in frappe.get_all("Dynamic Link", filters={"parenttype": "Address", "link_doctype": party_type, "link_name": party}, fields=["parent"])]

	party_addresses = frappe.get_all("Address", filters={"name": ["in", party_links]}, fields=["name", "is_primary_address"])

	if party_addresses:
		for address in party_addresses:
			if address.is_primary_address:
				return address.name
		
		return party_addresses[0]["name"]
	
	else:
		return None

@frappe.whitelist()
def set_lost(dn):
	outstanding = frappe.db.get_value("Revenue", dn, "outstanding_amount")
	frappe.db.set_value("Revenue", dn, "outstanding_amount", 0)
	frappe.db.set_value("Revenue", dn, "declared_lost", outstanding)

	doc = frappe.get_doc("Revenue", dn)
	doc.set_status(update=True)

	return doc

@frappe.whitelist()
def revert_lost(dn):
	outstanding = frappe.db.get_value("Revenue", dn, "declared_lost")
	frappe.db.set_value("Revenue", dn, "outstanding_amount", outstanding)
	frappe.db.set_value("Revenue", dn, "declared_lost", 0)

	doc = frappe.get_doc("Revenue", dn)
	doc.set_status(update=True)

	return doc

def get_list_context(context=None):
	from maia.controllers.website_list_for_contact import get_list_context
	list_context = get_list_context(context)
	list_context.update({
		'show_sidebar': True,
		'show_search': True,
		'no_breadcrumbs': True,
		'title': _('Receipts'),
	})

	return list_context

def get_permission_query_conditions(user):
	return get_accounting_query_conditions("Revenue", user)