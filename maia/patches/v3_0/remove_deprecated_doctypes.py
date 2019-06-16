# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.delete_doc("DocType", "Personal Debit")
	frappe.delete_doc("DocType", "Meal Expense")
	frappe.delete_doc("DocType", "Social Contribution")
	frappe.delete_doc("DocType", "Social Contribution Item")
	frappe.delete_doc("DocType", "Cash Deposit")
	frappe.delete_doc("DocType", "Fee Retrocession")
	frappe.delete_doc("Page", "maia-standard-letter")