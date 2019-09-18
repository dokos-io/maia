# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# License: See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.local.lang = 'fr'
	records = [
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 7,5', 'basic_price': 21, 'billing_price': 21, 'codification_name': 'SF 7,5', 'codification_description': 'Rééducation périnéale'}
	]

	for r in records:
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise
