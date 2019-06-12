# Copyright (c) 2019, Dokos and contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _


def get_context(context):
	context.show_sidebar = True
	context.doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)
	context.currency = maia.get_default_currency()
	if hasattr(context.doc, "set_indicator"):
		context.doc.set_indicator()

	context.title = frappe.form_dict.name

	default_print_format = frappe.db.get_value('Property Setter', dict(property='default_print_format', doc_type=frappe.form_dict.doctype), "value")
	if default_print_format:
		context.print_format = default_print_format
	else:
		context.print_format = "Facture Maia"

	if not frappe.has_website_permission(context.doc):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)