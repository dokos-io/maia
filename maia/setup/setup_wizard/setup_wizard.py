# coding=utf-8

# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe
from frappe import _
from .operations import install_fixtures, taxes_setup, defaults_setup, company_setup, maia_setup

def get_setup_stages(args=None):
	if frappe.db.sql("select name from tabCompany"):
		stages = [
			{
				'status': _('Wrapping up'),
				'fail_msg': _('Failed to login'),
				'tasks': [
					{
						'fn': fin,
						'args': args,
						'fail_msg': _("Failed to login")
					}
				]
			}
		]
	else:
		stages = [
		{
				'status': _('Setting up Maia'),
				'fail_msg': _('Failed to install presets'),
				'tasks': [
					{
						'fn': fixtures_stage,
						'args': args,
						'fail_msg': _("Failed to install presets")
					}
				]
			},
			{
				'status': _('Setting up company and taxes'),
				'fail_msg': _('Failed to setup company'),
				'tasks': [
					{
						'fn': setup_company,
						'args': args,
						'fail_msg': _("Failed to setup company")
					},
					{
						'fn': setup_taxes,
						'args': args,
						'fail_msg': _("Failed to setup taxes")
					}
				]
			},
			{
				'status': _('Setting defaults'),
				'fail_msg': 'Failed to set defaults',
				'tasks': [
					{
						'fn': setup_defaults,
						'args': args,
						'fail_msg': _("Failed to set defaults")
					}
				]
			},
			{
				'status': _('Setting email digest and logo'),
				'fail_msg': _('Failed to create email digest and logo'),
				'tasks': [
					{
						'fn': setup_brand,
						'args': args,
						'fail_msg': _("Failed to create email digest and logo")
					}
				]
			},
			{
				'status': _('Finish setup'),
				'fail_msg': _('Failed to install Maia'),
				'tasks': [
					{
						'fn': setup_maia,
						'args': args,
						'fail_msg': _("Failed to install Maia")
					}
				]
			},
			{
				'status': _('Wrapping up'),
				'fail_msg': _('Failed to login'),
				'tasks': [
					{
						'fn': fin,
						'args': args,
						'fail_msg': _("Failed to login")
					}
				]
			}
		]

	return stages

def setup_complete(args=None):
	fixtures_stage(args)
	frappe.db.commit()

	setup_company(args)
	setup_taxes(args)
	setup_defaults(args)
	setup_brand(args)
	setup_maia(args)
	fin(args)

def fixtures_stage(args):
	install_fixtures.install(args.get("country"))

def setup_company(args):
	defaults_setup.create_price_lists(args)
	company_setup.create_fiscal_year_and_company(args)
	company_setup.create_bank_account(args)

def setup_taxes(args):
	taxes_setup.create_sales_tax(args)
	maia_setup.create_midwife_tax_template(args)

def setup_defaults(args):
	defaults_setup.create_employee_for_self(args)
	defaults_setup.set_default_settings(args)
	defaults_setup.create_territories()
	defaults_setup.create_feed_and_todo()
	defaults_setup.set_no_copy_fields_in_variant_settings()

def setup_brand(args):
	company_setup.create_email_digest()
	company_setup.create_logo(args)

def setup_maia(args):
	install_fixtures.codifications(args.get("country"))
	install_fixtures.purchase_items(args.get("country"))
	install_fixtures.asset_categories(args.get("country"))
	maia_setup.create_professional_contact_card(args)
	maia_setup.create_item_groups(args)
	maia_setup.create_purchase_items(args)
	maia_setup.social_security_account(args)
	maia_setup.setup_asset_categories_accounts(args)
	maia_setup.set_mode_of_payment_account(args)
	maia_setup.set_initial_icons_list(args)
	maia_setup.correct_midwife_accounts(args)
	maia_setup.set_default_print_formats()
	maia_setup.add_terms_and_conditions()
	maia_setup.make_web_page(args)
	maia_setup.web_portal_settings()
	maia_setup.disable_signup()
	maia_setup.disable_guest_access()

def fin(args):
	frappe.local.message_log = []
	login_as_first_user(args)


def login_as_first_user(args):
	if args.get("email") and hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.login_as(args.get("email"))

def log_error(traceback, args):
	frappe.logger().debug(traceback)
	frappe.logger().debug(args)
