# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dokos and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from bs4 import BeautifulSoup

@frappe.whitelist()
def save_print_format(name, doctype, formatted_data, disabled, signature):
	clean_format = cleanup_format(formatted_data, doctype, signature)

	doc = frappe.get_doc("Maia Standard Letter", name)
	doc.editor_data = formatted_data
	doc.print_data = clean_format
	doc.disabled = disabled
	doc.signature = signature
	doc.save()
	
	return doc


def cleanup_format(html, doctype, signature):

	soup = BeautifulSoup(html, "html.parser")
	fields = soup.find_all('span', {'class': 'fieldlabel'})

	dts = []

	for f in fields:
		new_tag = soup.new_tag("span")

		if f.has_attr('data-function'):
			if f['data-function'] == "midwife":
				practitioners = "{% set practitioners = frappe.get_all('Professional Information Card', filters = {'user': frappe.session.user}, fields = ['name']) %}"
				practitioner_inner = "{%- for practitioner in practitioners -%}"
				practitioner_end = "{%- endfor -%}"
				practitioner = "{{ practitioner.name }}"
				new_tag.append(practitioners)
				new_tag.append(practitioner_inner)
				new_tag.append(practitioner)
				new_tag.append(practitioner_end)
				f.replace_with(new_tag)

			elif f['data-function'] == "current_date":
				new_tag.string = "{% set today = frappe.utils.getdate(frappe.utils.nowdate()) %}{{ frappe.format_date(today) }}"
				f.replace_with(new_tag)

		else:
			if f['data-doctype'] == doctype:
				docname = 'doc'
			else:
				if f['data-doctype'] not in dts:
					dts.append({f['data-doctype']: f['data-reference']})
				docname = f['data-doctype'].replace(" ", "").lower()
			
			if f['data-fieldtype'] == "Date":
				new_tag.string = "{{" + " frappe.format_date({0}.{1}) ".format(docname, f['data-fieldname']) + "or '' }}"
				f.replace_with(new_tag)
			else:
				new_tag.string = "{{" + " {0}.{1} ".format(docname, f['data-fieldname']) + "or '' }}"
				f.replace_with(new_tag)

	for dt in dts:
		for k in dt:
			key = k
			reference = dt[k]
		docname = key.replace(" ", "").lower()
		get_doc = "{%" + " set {0} = frappe.get_doc('{1}', {2}) ".format(docname, key, reference) + "%}"	
		soup.div.insert_before(get_doc)

	if soup.div:
		letterhead = soup.new_tag("div", **{"class":"letter-head"})
		letterhead.string = "{{ letter_head }}"
		soup.div.insert_before(letterhead)


	if signature:
		signature = soup.new_tag("div")
		signature_outer = soup.new_tag("div", **{"class":"row text-center"})
		signature_inner = soup.new_tag("div", **{"class":"col-xs-5 col-xs-offset-7"})
		signature_inner.append(soup.new_tag("img", src="{{practitioner.signature}}", height="200px", width="200px"))
		signature_outer.append(signature_inner)
		signature.append(signature_outer)
		signature_outer.insert_before("{% set practitioners = frappe.get_all('Professional Information Card', filters = {'user': frappe.session.user}, fields = ['signature']) %}")
		signature_outer.insert_before("{%- for practitioner in practitioners -%}")
		signature_outer.insert_before("{% if practitioner.signature %}")
		signature_outer.insert_before(soup.new_tag("br"))
		signature_outer.insert_after("{%- endfor -%}")
		signature_outer.insert_after("{% endif %}")

		soup.append(signature)

	return str(soup)