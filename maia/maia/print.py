# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt 

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint
from frappe.utils.pdf import get_pdf
from six import string_types
from frappe.www.printview import get_html, validate_print_permission, get_letter_head, convert_markdown, make_layout


@frappe.whitelist()
def print_prescription(doctype, doc, as_print, print_format):
	if cint(as_print):
		return frappe.get_print(doctype, doc, print_format = print_format)
	else:
		frappe.throw(_("Print Error: Please contact the technical support."))

@frappe.whitelist()
def download_standard_letter_pdf(doctype, name, template='Standard', doc=None, no_letterhead=0):
	html = get_html_and_style(doctype, name, template)
	frappe.local.response.filename = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
	frappe.local.response.filecontent = get_pdf(html)
	frappe.local.response.type = "download"


@frappe.whitelist()
def get_html_and_style(doc, name=None, template=None, no_letterhead=None, trigger_print=False, style=None, lang=None):
	"""Returns `html` and `style` of print format, used in PDF etc"""

	if isinstance(doc, string_types) and isinstance(name, string_types):
		doc = frappe.get_doc(doc, name)

	if isinstance(doc, string_types):
		doc = frappe.get_doc(json.loads(doc))

	print_format = frappe.get_doc("Maia Standard Letter", template)
	frappe.log_error(print_format)

	return get_html(doc, name=name, print_format=print_format, no_letterhead=no_letterhead, trigger_print=trigger_print)

def get_html(doc, name=None, print_format=None, meta=None, no_letterhead=None, trigger_print=False):

	print_settings = frappe.db.get_singles_dict("Print Settings")

	doc.flags.in_print = True

	#if not frappe.flags.ignore_print_permissions:
	#	validate_print_permission(doc)

	if doc.meta.is_submittable:
		if doc.docstatus==0 and not cint(print_settings.allow_print_for_draft):
			frappe.throw(_("Not allowed to print draft documents"), frappe.PermissionError)

		if doc.docstatus==2 and not cint(print_settings.allow_print_for_cancelled):
			frappe.throw(_("Not allowed to print cancelled documents"), frappe.PermissionError)

	if hasattr(doc, "before_print"):
		doc.before_print()

	if not hasattr(doc, "print_heading"): doc.print_heading = None
	if not hasattr(doc, "sub_heading"): doc.sub_heading = None

	if not meta:
		meta = frappe.get_meta(doc.doctype)

	jenv = frappe.get_jenv()

	template = jenv.from_string(print_format.print_data)

	letter_head = frappe._dict(get_letter_head(doc, no_letterhead) or {})

	if letter_head.content:
		letter_head.content = frappe.utils.jinja.render_template(letter_head.content, {"doc": doc.as_dict()})

	if letter_head.footer:
		letter_head.footer = frappe.utils.jinja.render_template(letter_head.footer, {"doc": doc.as_dict()})

	convert_markdown(doc, meta)

	args = {
		"doc": doc,
		"meta": frappe.get_meta(doc.doctype),
		"no_letterhead": 0,
		"trigger_print": cint(trigger_print),
		"letter_head": letter_head.content,
		"footer": letter_head.footer,
		"print_settings": frappe.get_doc("Print Settings")
	}

	html = template.render(args, filters={"len": len})

	if cint(trigger_print):
		html += trigger_print_script

	frappe.log_error(html)

	return html