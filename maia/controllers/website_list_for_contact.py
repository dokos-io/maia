# Copyright (c) 2019, Dokos and contributors
# See license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt, has_common
from frappe.utils.user import is_website_user

def get_list_context(context=None):
	return {
		"global_number_format": frappe.db.get_default("number_format") or "#,###.##",
		"currency": frappe.db.get_default("currency"),
		"currency_symbols": json.dumps(dict(frappe.db.sql("""select name, symbol
			from tabCurrency where enabled=1"""))),
		"row_template": "templates/includes/transaction_row.html",
		"get_list": get_transaction_list
	}

def get_transaction_list(doctype, txt=None, filters=None, limit_start=0, limit_page_length=20, order_by="modified"):
	user = frappe.session.user
	key = None

	if not filters: filters = []

	filters.append((doctype, "docstatus", "=", 1))

	if (user != "Guest" and is_website_user()):
		parties_doctype = doctype
		# find party for this contact
		patients = get_patients(parties_doctype, user)

		if not patients: return []

		key, parties = get_party_details(patients)
		print(key, parties)

		filters.append((doctype, key, "in", parties))

		if key:
			return post_process(doctype, get_list_for_transactions(doctype, txt,
				filters=filters, fields="name",limit_start=limit_start,
				limit_page_length=limit_page_length,ignore_permissions=True,
				order_by="modified desc"))
		else:
			return []

	return post_process(doctype, get_list_for_transactions(doctype, txt, filters, limit_start, limit_page_length,
		fields="name", order_by="modified desc"))

def get_list_for_transactions(doctype, txt, filters, limit_start, limit_page_length=20,
	ignore_permissions=False,fields=None, order_by=None):
	""" Get List of transactions like Invoices, Orders """
	from frappe.www.list import get_list
	meta = frappe.get_meta(doctype)
	data = []
	or_filters = []

	for d in get_list(doctype, txt, filters=filters, fields="name", limit_start=limit_start,
		limit_page_length=limit_page_length, ignore_permissions=ignore_permissions, order_by="modified desc"):
		data.append(d)

	if txt:
		if meta.get_field('codifications'):
			if meta.get_field('codifications').options:
				child_doctype = meta.get_field('codifications').options
				for item in frappe.get_all(child_doctype, {"codification": ['like', "%" + txt + "%"]}):
					child = frappe.get_doc(child_doctype, item.name)
					or_filters.append([doctype, "name", "=", child.parent])

	if or_filters:
		for r in frappe.get_list(doctype, fields=fields,filters=filters, or_filters=or_filters,
			limit_start=limit_start, limit_page_length=limit_page_length, 
			ignore_permissions=ignore_permissions, order_by=order_by):
			data.append(r)

	return data

def get_party_details(patients):
	if patients:
		key, parties = "patient", patients
	else:
		key, parties = "patient", []

	return key, parties

def post_process(doctype, data):
	result = []
	for d in data:
		doc = frappe.get_doc(doctype, d.name)

		if hasattr(doc, "set_indicator"):
			doc.set_indicator()

		doc.items_preview = ", ".join([d.codification for d in doc.codifications if d.codification])

		result.append(doc)

	return result

def get_patients(doctype, user):
	patients = []
	meta = frappe.get_meta(doctype)

	if has_common(["Patient"], frappe.get_roles(user)):
		patients = [p.name for p in frappe.get_all("Patient Record", dict(website_user=user))] \
			if meta.get_field("patient") else None

	return patients

def has_website_permission(doc, ptype, user, verbose=False):
	doctype = doc.doctype
	patients = get_patients(doctype, user)
	if patients:
		return frappe.get_all(doctype, filters=[(doctype, "patient", "in", patients),
			(doctype, "name", "=", doc.name)]) and True or False
	else:
		return False
