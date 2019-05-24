# Copyright (c) 2017, DOKOS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.model
import frappe.utils
import json, os


@frappe.whitelist()
def get_practitioner(doctype, name=None, filters=None):
	'''Returns a document by name or filters
	:param doctype: DocType of the document to be returned
	:param name: return document of this `name`
	:param filters: If name is not set, filter by these values and return the first match'''
	if filters and not name:
		name = frappe.db.get_value(doctype, json.loads(filters))
		if not name:
			name = None

	if name is not None:
		return frappe.get_doc(doctype, name).as_dict()
