# Copyright (c) 2019, Dokos and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe
import json

def make():
	frappe.flags.mute_emails = True
	
	setup_demo_page()
	setup_user()
	setup_user_roles()
	frappe.db.commit()
	frappe.clear_cache()

	site = frappe.local.site
	frappe.destroy()
	frappe.init(site)
	frappe.connect()

def setup_demo_page():
	website_settings = frappe.db.set_value("Website Settings", "Website Settings", "home_page", "demo")

def setup_user():
	frappe.db.sql('delete from tabUser where name not in ("Guest", "Administrator")')
	for u in json.loads(open(frappe.get_app_path('maia', 'demo', 'user.json')).read()):
		user = frappe.new_doc("User")
		user.update(u)
		user.flags.no_welcome_mail = True
		user.new_password = 'Demo1234567!!!'
		user.insert()

def setup_user_roles():
	user = frappe.get_doc('User', 'demo@maia-by-dokos.fr')
	user.add_roles('Midwife', 'Patient', 'Midwife Substitute', 'Appointment User')