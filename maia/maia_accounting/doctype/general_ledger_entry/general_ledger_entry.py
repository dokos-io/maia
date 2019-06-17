# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia_accounting.utils import get_accounting_query_conditions

class GeneralLedgerEntry(Document):
	pass

def make_gl_entries(gl_entries):
	for entry in gl_entries:
		gl = frappe.new_doc("General Ledger Entry")
		gl.update(entry)
		gl.insert()
		gl.submit()

def get_permission_query_conditions(user):
	return get_accounting_query_conditions("General Ledger Entry", user)