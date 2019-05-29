# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class DefaultTemplate(Document):
	def validate(self):
		self.build_new_website()
		self.build_new_theme()
		update_settings()

	def build_new_website(self):
		main_section = self.build_main_section()
		script = self.build_script()

		if frappe.db.exists("Web Page", dict(route="home", title=self.website_title)):
			page = frappe.get_doc("Web Page", dict(route="home", title=self.website_title))
		else:
			page = frappe.new_doc("Web Page")

		page.title = self.website_title
		page.route = "home"
		page.published = 1
		page.show_title = 0
		page.content_type = "HTML"
		page.main_section_html = main_section
		page.insert_code = 1
		page.javascript = script

		page.save(ignore_permissions = True)

	def build_new_theme(self):
		style = self.build_style()

		if frappe.db.exists("Website Theme", "Maia"):
			theme = frappe.get_doc("Website Theme", "Maia")
			theme.theme_scss = style
			theme.save()

		else:
			theme = frappe.get_doc({
				"doctype": "Website Theme",
				"theme": "Maia",
				"theme_scss": style
			})

			theme.insert(ignore_permissions=True)

	def build_main_section(self):
		return frappe.render_template('/templates/includes/web_templates/maia/maia.html', {'data':self})

	def build_style(self):
		return frappe.render_template('/templates/includes/web_templates/maia/style.html', {"data": self})

	def build_script(self):
		return frappe.render_template('/templates/includes/web_templates/maia/script.html', {"data": self})

@frappe.whitelist()
def update_instructions():
	return frappe.render_template('/templates/includes/web_templates/maia/template_instructions.html', {'data':'data'})

def update_settings():
	settings = frappe.get_doc("Website Settings", None)

	settings.home_page = "home"
	settings.website_theme = "Maia"
	settings.top_bar_items = []
	settings.head_html = build_head()
	settings.extend('top_bar_items', 
		[{
			"label": _("Appointments"),
			"parent_label": "",
			"url": "/appointment",
			"target": "",
			"right": 1
		},
		{
			"label": _("Contact Us"),
			"parent_label": "",
			"url": "/contact",
			"target": "",
			"right": 1
		}])
	settings.save(ignore_permissions = True)

def build_head():
	return frappe.render_template('/templates/includes/web_templates/maia/head.html', {})