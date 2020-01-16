# coding=utf-8
# Copyright (c) 2018, DOKOS and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import os

def install_chart_of_accounts():
	path = os.path.join(frappe.get_module_path('maia_accounting'), "doctype", "accounting_item", "plan_comptable.json")
	pc = frappe.get_file_json(path) 
	for p in pc: 
		try: 
			doc = frappe.new_doc("Accounting Item") 
			doc.accounting_item = p 
			doc.update(pc[p]) 
			doc.insert(ignore_permissions=True) 
		except Exception as e: 
			print(e)

	frappe.db.commit()

def add_fiscal_years():
	fiscal_years = [
		{"year": 2017, "start": "2017-01-01", "end": "2017-12-31"},
		{"year": 2018, "start": "2018-01-01", "end": "2018-12-31"},
		{"year": 2019, "start": "2019-01-01", "end": "2019-12-31"},
		{"year": 2020, "start": "2020-01-01", "end": "2020-12-31"}
	]

	for fy in fiscal_years:
		try:
			frappe.get_doc({
				"doctype": "Maia Fiscal Year",
				"year": fy["year"],
				"year_start_date": fy["start"],
				"year_end_date": fy["end"]
			}).insert(ignore_permissions=True)
		except Exception as e:
			print(e)

def add_meal_expense_deductions():
	deductions = [
		{"fiscal_year": 2016, "deductible_amount": 4.70, "limit": 18.3},
		{"fiscal_year": 2017, "deductible_amount": 4.75, "limit": 18.4},
		{"fiscal_year": 2018, "deductible_amount": 4.80, "limit": 18.6},
		{"fiscal_year": 2019, "deductible_amount": 4.85, "limit": 18.8},
		{"fiscal_year": 2020, "deductible_amount": 4.90, "limit": 19.0}
	]

	for d in deductions:
		doc = frappe.get_doc({
			"doctype": "Meal Expense Deduction",
			"fiscal_year": d["fiscal_year"],
			"deductible_amount": d["deductible_amount"],
			"limit": d["limit"]
		})
		doc.insert()
		doc.submit()

def set_default_print_formats():
	names = ["Patient Folder", "Prenatal Interview Folder", "Perineum Rehabilitation Folder", "Gynecology Folder", \
		"Pregnancy Folder", "Postnatal Consultation", "Birth Preparation Consultation", "Perineum Rehabilitation Consultation", \
		"Free Consultation", "Early Postnatal Consultation", "Gynecological Consultation", "Pregnancy Consultation", "Drug Prescription",
		"Facture Maia", "Prenatal Interview Consultation"]

	for name in names:
		print_format = frappe.get_doc("Print Format", name)
		frappe.make_property_setter({
			'doctype_or_field': "DocType",
			'doctype': print_format.doc_type,
			'property': "default_print_format",
			'value': name,
		})

def make_web_page():
	default_template = frappe.get_doc('Default Template', None)
	default_template.website_title = _("Welcome")
	default_template.title = _("Welcome")
	default_template.subtitle = _("Please login to make an appointment")
	default_template.button_label = _("Make an appointment")
	default_template.button_link = "/login"
	default_template.save()

def web_portal_settings():
	frappe.reload_doctype("Portal Settings")
	items = frappe.get_all("Portal Menu Item", fields=['name', 'title', 'route', 'enabled'])

	for item in items:
		if not (item.route == "/appointment" or item.route == "/my-appointments"):
			frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

	frappe.db.commit()

def disable_signup():
	frappe.db.set_value("Website Settings", "Website Settings", "disable_signup", 1)
	frappe.db.commit()

def disable_guest_access():
	frappe.db.set_value("Role", "Guest", "desk_access", 0)
	frappe.db.commit()