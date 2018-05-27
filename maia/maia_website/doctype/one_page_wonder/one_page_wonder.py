# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OnePageWonder(Document):
	pass

@frappe.whitelist()
def update_instructions():
	return frappe.render_template('/templates/includes/web_templates/template_instructions.html', {'data':'data'})

@frappe.whitelist()
def update_website():
	build_new_website()
	update_theme()
	update_settings()

def build_new_website():
	main_section = build_main_section()

	if frappe.db.exists("Web Page", "home-page"):
		frappe.delete_doc("Web Page", "home-page")

	page = frappe.get_doc({
		"doctype": "Web Page",
		"title": "Home Page",
		"route": "index",
		"published": 1,
		"show_title": 1,
		"main_section": main_section,
		"insert_code": 1
	})

	page.insert(ignore_permissions = True)

def build_main_section():
	template = frappe.get_doc("One Page Wonder", None)
	return frappe.render_template('/templates/includes/web_templates/one_page_wonder/one_page_wonder.html', {'data':template})

def update_theme():
	if frappe.db.exists("Website Theme", "One Page Wonder"):
		frappe.db.set_value("Website Settings", None, "website_theme", None)
		frappe.delete_doc("Website Theme", "One Page Wonder")

	template = frappe.get_doc("One Page Wonder", None)
	style  = frappe.render_template('/templates/includes/web_templates/one_page_wonder/style.html', {"data": template})

	js = frappe.render_template('/templates/includes/web_templates/one_page_wonder/script.html', {"data": "data"})

	theme = frappe.get_doc({
		"doctype": "Website Theme",
		"theme": "One Page Wonder",
		"apply_style": 1,
		"css": style,
		"js": js,
		"top_bar_color": "#333",
		"top_bar_text_color": "#FFF"
	})
	theme.insert(ignore_permissions = True)

def update_settings():
	settings = frappe.get_doc("Website Settings", None)
	data = {
	"title": frappe.db.get_value("Homepage", None, "title")
	}
	head_html = frappe.render_template('/templates/includes/web_templates/one_page_wonder/header.html', {'data':data})


	settings.home_page = "index"
	settings.website_theme = "One Page Wonder"
	settings.head_html = head_html
	settings.top_bar_items = []
	settings.append('top_bar_items', {
		"label": "Prendre Rendez-Vous",
		"parent_label": "",
		"url": "/appointment",
		"target": "",
		"right": 1
	})
	settings.save(ignore_permissions = True)
