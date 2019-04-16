# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GeneralLedgerEntry(Document):
	pass


def make_gl_entries(gl_entries, cancel=False):
	if not cancel:
		for entry in gl_entries:
			gl = frappe.new_doc("General Ledger Entry")
			gl.update(entry)
			print(gl.__dict__)
			gl.insert()
			gl.submit()
	else:
		pass
