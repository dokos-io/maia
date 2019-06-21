# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class BankStatementBalance(Document):
	pass

@frappe.whitelist()
def update_balance(**kwargs):
	bank_account = kwargs.get("bank_account")
	try:
		docs = []
		for d in ["start_date", "end_date"]:
			if kwargs.get(d):
				docs.append({
					"doctype": "Bank Statement Balance",
					"bank_account": bank_account,
					"date": kwargs.get(d),
					"balance": kwargs.get("start_balance") or 0 if d == "start_date" else kwargs.get("end_balance") or 0
				})

		for doc in docs:
			if frappe.db.exists(doc["doctype"], {"date": getdate(doc["date"]), "bank_account": doc["bank_account"]}):
				existing_entry = frappe.get_doc(doc["doctype"], {"date": doc["date"], "bank_account": doc["bank_account"]})
				if existing_entry.balance == doc["balance"]:
					continue
				else:
					existing_entry.cancel()
					existing_entry.delete()
					balance = frappe.get_doc(doc)
					balance.insert()
					balance.submit()

			else:
				balance = frappe.get_doc(doc)
				balance.insert()
				balance.submit()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Bank balance update error")