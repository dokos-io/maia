# coding=utf-8

# Copyright (c) 2019, DOKOS and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
from frappe import _
from .operations import install_fixtures, defaults_setup, maia_setup

def setup_complete():
	frappe.local.lang = "fr"
	maia_setup.install_chart_of_accounts()
	fixtures_stage()
	frappe.db.commit()

	setup_defaults()
	setup_maia()
	frappe.db.commit()

def fixtures_stage():
	install_fixtures.install("France")

def setup_defaults():
	defaults_setup.set_default_settings()

def setup_maia():
	install_fixtures.codifications()
	maia_setup.add_fiscal_years()
	maia_setup.add_meal_expense_deductions()
	maia_setup.create_professional_contact_card()
	maia_setup.set_default_print_formats()
	maia_setup.make_web_page()
	maia_setup.web_portal_settings()
	maia_setup.disable_signup()
	maia_setup.disable_guest_access()
	maia_setup.send_welcome_email()
