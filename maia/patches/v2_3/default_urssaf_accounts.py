# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	companies = frappe.get_all("Company")

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")
		social_contribution_deductible_account = "6451 - Cotisations à l'URSSAF - " + abbr
		social_contributions_third_party = "URSSAF"
		try:
			if frappe.db.exists('Account', social_contribution_deductible_account):
				frappe.db.set_value('Company', company.name, 'social_contribution_deductible_account', social_contribution_deductible_account)

			if frappe.db.exists('Supplier', social_contributions_third_party):
				frappe.db.set_value('Company', company.name, 'social_contributions_third_party', social_contributions_third_party)
		except Exception as e:
			print(e)


		acc = frappe.get_doc("Account", "431 - Sécurité sociale - " + abbr)
		acc.parent_account = "43 - Sécurité sociale et autres organismes sociaux créditeurs - " + abbr
		acc.save()
