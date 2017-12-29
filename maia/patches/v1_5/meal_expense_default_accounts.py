# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
	companies = frappe.get_all("Company")

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")

		meal_expense_deductible_account = "625700-Frais de réceptions déductibles - " + abbr
		meal_expense_non_deductible_account = "625710-Frais de réceptions non déductibles - " + abbr

		if frappe.db.exists('Account', meal_expense_deductible_account):
			frappe.db.set_value('Company', company.name, 'meal_expense_deductible_account', meal_expense_deductible_account)

		if frappe.db.exists('Account', meal_expense_non_deductible_account):
			frappe.db.set_value('Company', company.name, 'meal_expense_non_deductible_account', meal_expense_non_deductible_account)

		frappe.db.commit()
