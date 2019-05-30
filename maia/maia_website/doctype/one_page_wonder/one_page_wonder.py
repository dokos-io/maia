# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class OnePageWonder(Document):
	def validate(self):
		self.build_new_website()
		self.build_new_theme()
		update_settings()

	def build_new_website(self):
		main_section = self.build_main_section()
		script = self.build_script()

		if frappe.db.exists("Web Page", dict(route="index")):
			page = frappe.get_doc("Web Page", dict(route="index"))
		else:
			page = frappe.new_doc("Web Page")

		page.title = self.website_title
		page.route = "index"
		page.published = 1
		page.show_title = 0
		page.content_type = "HTML"
		page.main_section_html = main_section
		page.insert_code = 1
		page.javascript = script

		page.save(ignore_permissions = True)

	def build_new_theme(self):
		style = self.build_style()

		if frappe.db.exists("Website Theme", "One Page Wonder"):
			theme = frappe.get_doc("Website Theme", "One Page Wonder")
			theme.theme_scss = style
			theme.save()

		else:
			theme = frappe.get_doc({
				"doctype": "Website Theme",
				"theme": "One Page Wonder",
				"theme_scss": style
			})

			theme.insert(ignore_permissions=True)

	def build_main_section(self):
		return frappe.render_template('/templates/includes/web_templates/one_page_wonder/one_page_wonder.html', {'data':self})

	def build_style(self):
		return frappe.render_template('/templates/includes/web_templates/one_page_wonder/style.html', {"data": self})

	def build_script(self):
		return frappe.render_template('/templates/includes/web_templates/one_page_wonder/script.html', {"data": self})

@frappe.whitelist()
def update_instructions():
	return frappe.render_template('/templates/includes/web_templates/one_page_wonder/template_instructions.html', {'data':'data'})

def update_settings():
	settings = frappe.get_doc("Website Settings", None)

	settings.home_page = "index"
	settings.website_theme = "One Page Wonder"
	settings.top_bar_items = []
	settings.append('top_bar_items', {
		"label": _("Appointments"),
		"parent_label": "",
		"url": "/appointment",
		"target": "",
		"right": 1
	})
	settings.save(ignore_permissions = True)
