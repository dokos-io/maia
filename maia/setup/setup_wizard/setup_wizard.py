# coding=utf-8

# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe
import copy

import os
import json
from frappe.utils import cstr, flt, getdate
from frappe import _
from frappe.utils.file_manager import save_file
import install_fixtures
from erpnext.accounts.doctype.account.account import RootNotEditable
from frappe.core.doctype.communication.comment import add_info_comment
from frappe.desk.doctype.desktop_icon.desktop_icon import set_hidden_list
from frappe.printing.doctype.print_format.print_format import make_default

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
				'fail_msg': _('Failed to install Maia'),
				'tasks': [
					{
						'fn': setup_complete,
						'args': args,
						'fail_msg': _("Failed to install Maia")
					}
				]
			}
		]

	return stages

def setup_complete(args=None):
	install_fixtures.install(args.get("country"))

	create_price_lists(args)
	create_fiscal_year_and_company(args)
	create_sales_tax(args)
	create_users(args)
	set_defaults(args)
	create_professional_contact_card(args)
	create_territories()
	create_feed_and_todo()
	create_email_digest()
	create_letter_head(args)
	create_taxes(args)
	create_items(args)
	create_customers(args)
	create_suppliers(args)
	create_midwife_tax_template(args)
	create_item_groups(args)

	install_fixtures.codifications(args.get("country"))
	install_fixtures.purchase_items(args.get("country"))
	install_fixtures.asset_categories(args.get("country"))
	social_security_account(args)

	create_purchase_items(args)
	setup_asset_categories_accounts(args)

	create_logo(args)

	frappe.local.message_log = []

	frappe.db.commit()
	login_as_first_user(args)

	frappe.db.commit()
	frappe.clear_cache()

	set_mode_of_payment_account(args)
	frappe.db.commit()

	correct_midwife_accounts(args)

	initial_list = ['Stock', 'Manufacturing', 'Learn', 'Buying', 'Selling', 'Support', 'Integrations', 'Maintenance', 'Schools', 'HR', 'CRM', 'Supplier', 'Employee', 'Issue',
					'Lead', 'POS', 'Student', 'Student Group', 'Course Schedule', 'Student Attendance', 'Course', 'Program', 'Student Applicant', 'Fees', 'Instructor', 'Room', 'Leaderboard',
					'Student Attendance Tool', 'Education', 'Healthcare', 'Hub', 'Data Import', 'Restaurant', 'Agriculture', 'Crop', 'Crop Cycle', 'Fertilizer', 'Land Unit', 'Disease', 'Plant Analysis',
					'Soil Analysis', 'Soil Texture', 'Water Analysis', 'Weather', 'Grant Application', 'Donor', 'Volunteer', 'Member', 'Chapter', 'Non Profit']
	hidden_list = []

	for i in initial_list:
		try:
			frappe.get_doc('Desktop Icon', {'standard': 1, 'label': i})
			hidden_list.append(i)
		except Exception:
			pass

	set_hidden_list(hidden_list)

	set_default_print_formats()
	add_terms_and_conditions()
	make_web_page(args)
	web_portal_settings()
	disable_signup()
	fin(args)


def fin(args):
	frappe.local.message_log = []
	login_as_first_user(args)


def login_as_first_user(args):
	if args.get("email") and hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.login_as(args.get("email"))

def create_fiscal_year_and_company(args):
	if (args.get('fy_start_date')):
		curr_fiscal_year = get_fy_details(
			args.get('fy_start_date'), args.get('fy_end_date'))
		frappe.get_doc({
			"doctype": "Fiscal Year",
			'year': curr_fiscal_year,
			'year_start_date': args.get('fy_start_date'),
			'year_end_date': args.get('fy_end_date'),
		}).insert()
		args["curr_fiscal_year"] = curr_fiscal_year

	# Company
	if (args.get('company_name')):
		frappe.get_doc({
			"doctype": "Company",
			'company_name': args.get('company_name').strip(),
			'abbr': args.get('company_abbr'),
			'default_currency': args.get('currency'),
			'country': args.get('country'),
			'create_chart_of_accounts_based_on': 'Standard Template',
			'chart_of_accounts': args.get('chart_of_accounts'),
			'domain': args.get('domain'),
			'email': args.get('company_email'),
			'phone_no': args.get('company_phone')
		}).insert()

		# Enable shopping cart
		enable_shopping_cart(args)

		# Bank Account
		create_bank_account(args)


def enable_shopping_cart(args):
	frappe.get_doc({
		"doctype": "Shopping Cart Settings",
		"enabled": 1,
		'company': args.get('company_name').strip(),
		'price_list': frappe.db.get_value("Price List", {"selling": 1}),
		'default_customer_group': _("Individual"),
		'quotation_series': "QTN-",
	}).insert()


def create_bank_account(args):
	if args.get("bank_account"):
		default_bank_account = "5121 - Comptes en monnaie nationale - " + \
			args.get('company_abbr')
		company_name = args.get('company_name').strip()
		bank_account_group = frappe.db.get_value("Account",
												 {"name": default_bank_account, "account_type": "Bank", "is_group": 1, "root_type": "Asset",
												  "company": company_name})
		if bank_account_group:
			bank_account = frappe.get_doc({
				"doctype": "Account",
				'account_name': "512100 - " + args.get("bank_account"),
				'parent_account': bank_account_group,
				'is_group': 0,
				'company': company_name,
				"account_type": "Bank",
			})
			try:
				return bank_account.insert()
			except RootNotEditable:
				frappe.throw(_("Bank account cannot be named as {0}").format(
					args.get("bank_account")))
			except frappe.DuplicateEntryError:
				# bank account same as a CoA entry
				pass


def set_mode_of_payment_account(args):
	list_of_payment_modes = frappe.get_all('Mode of Payment', filters={
										   'type': 'Bank'}, fields=['name'])
	if args.get("bank_account"):
		default_bank_account = "512100 - " + \
			args.get("bank_account") + " - " + args.get('company_abbr')
	else:
		default_bank_account = "5121 - Comptes en monnaie nationale - " + \
			args.get('company_abbr')
	company_name = args.get('company_name').strip()
	for list_of_payment_mode in list_of_payment_modes:
		mode_of_payment = frappe.get_doc(
			'Mode of Payment', list_of_payment_mode.name)
		mode_of_payment.append('accounts', {
			'company': company_name,
			'default_account': default_bank_account
		})
		mode_of_payment.save(ignore_permissions=True)


def create_price_lists(args):
	for pl_type, pl_name in (("Selling", _("Standard Selling")), ("Buying", _("Standard Buying"))):
		frappe.get_doc({
			"doctype": "Price List",
			"price_list_name": pl_name,
			"enabled": 1,
			"buying": 1 if pl_type == "Buying" else 0,
			"selling": 1 if pl_type == "Selling" else 0,
			"currency": args["currency"]
		}).insert()


def set_defaults(args):
	# enable default currency
	frappe.db.set_value("Currency", args.get("currency"), "enabled", 1)

	global_defaults = frappe.get_doc("Global Defaults", "Global Defaults")
	global_defaults.update({
		'current_fiscal_year': args.get('curr_fiscal_year'),
		'default_currency': args.get('currency'),
		'default_company': args.get('company_name').strip(),
		"country": args.get("country"),
		'disable_rounded_total': 1
	})

	global_defaults.save()

	frappe.db.set_value("System Settings", None,
						"email_footer_address", args.get("company"))

	accounts_settings = frappe.get_doc("Accounts Settings")
	accounts_settings.auto_accounting_for_stock = 1
	accounts_settings.save()

	stock_settings = frappe.get_doc("Stock Settings")
	stock_settings.item_naming_by = "Item Code"
	stock_settings.valuation_method = "FIFO"
	stock_settings.default_warehouse = frappe.db.get_value(
		'Warehouse', {'warehouse_name': _('Stores')})
	stock_settings.stock_uom = _("Nos")
	stock_settings.auto_indent = 1
	stock_settings.auto_insert_price_list_rate_if_missing = 1
	stock_settings.automatically_set_serial_nos_based_on_fifo = 1
	stock_settings.save()

	selling_settings = frappe.get_doc("Selling Settings")
	selling_settings.cust_master_name = "Customer Name"
	selling_settings.so_required = "No"
	selling_settings.dn_required = "No"
	selling_settings.allow_multiple_items = 1
	selling_settings.save()

	buying_settings = frappe.get_doc("Buying Settings")
	buying_settings.supp_master_name = "Supplier Name"
	buying_settings.po_required = "No"
	buying_settings.pr_required = "No"
	buying_settings.maintain_same_rate = 1
	buying_settings.allow_multiple_items = 1
	buying_settings.save()

	notification_control = frappe.get_doc("Notification Control")
	notification_control.quotation = 1
	notification_control.sales_invoice = 1
	notification_control.purchase_order = 1
	notification_control.save()

	hr_settings = frappe.get_doc("HR Settings")
	hr_settings.emp_created_by = "Naming Series"
	hr_settings.save()

	# domain_settings = frappe.get_doc("Domain Settings")
	# domain_settings.append('active_domains', dict(domain=_(args.get('domain'))))
	# domain_settings.save()


def create_feed_and_todo():
	"""update Activity feed and create todo for creation of item, customer, vendor"""
	add_info_comment(**{
		"subject": _("Maia Setup Complete!")
	})


def create_email_digest():
	from frappe.utils.user import get_system_managers
	system_managers = get_system_managers(only_name=True)
	if not system_managers:
		return

	companies = frappe.db.sql_list("select name FROM `tabCompany`")
	for company in companies:
		if not frappe.db.exists("Email Digest", "Default Weekly Digest - " + company):
			edigest = frappe.get_doc({
				"doctype": "Email Digest",
				"name": "Default Weekly Digest - " + company,
				"company": company,
				"frequency": "Weekly",
				"recipient_list": "\n".join(system_managers)
			})

			for df in edigest.meta.get("fields", {"fieldtype": "Check"}):
				if df.fieldname != "scheduler_errors":
					edigest.set(df.fieldname, 1)

			edigest.insert()

	# scheduler errors digest
	if companies:
		edigest = frappe.new_doc("Email Digest")
		edigest.update({
			"name": "Scheduler Errors",
			"company": companies[0],
			"frequency": "Daily",
			"recipient_list": "\n".join(system_managers),
			"scheduler_errors": 1,
			"enabled": 1
		})
		edigest.insert()


def get_fy_details(fy_start_date, fy_end_date):
	start_year = getdate(fy_start_date).year
	if start_year == getdate(fy_end_date).year:
		fy = cstr(start_year)
	else:
		fy = cstr(start_year) + '-' + cstr(start_year + 1)
	return fy


def create_sales_tax(args):
	country_wise_tax = get_country_wise_tax(args.get("country"))
	if country_wise_tax and len(country_wise_tax) > 0:
		for sales_tax, tax_data in country_wise_tax.items():
			make_tax_account_and_template(args.get("company_name").strip(),
										  tax_data.get('account_name'), tax_data.get('tax_rate'), sales_tax)


def get_country_wise_tax(country):
	data = {}
	with open(os.path.join(os.path.dirname(__file__), "data", "country_wise_tax.json")) as countrywise_tax:
		data = json.load(countrywise_tax).get(country)

	return data


def create_taxes(args):
	for i in xrange(1, 6):
		if args.get("tax_" + str(i)):
			# replace % in case someone also enters the % symbol
			tax_rate = cstr(args.get("tax_rate_" + str(i))
							or "").replace("%", "")
			account_name = args.get("tax_" + str(i))

			make_tax_account_and_template(
				args.get("company_name").strip(), account_name, tax_rate)


def make_tax_account_and_template(company, account_name, tax_rate, template_name=None):
	try:
		account = make_tax_account(company, account_name, tax_rate)
		if account:
			make_sales_and_purchase_tax_templates(account, template_name)
	except frappe.NameError, e:
		if e.args[2][0] == 1062:
			pass
		else:
			raise
	except RootNotEditable, e:
		pass


def get_tax_account_group(company):
	tax_group = frappe.db.get_value("Account",
									{"account_name": "Duties and Taxes", "is_group": 1, "company": company})
	if not tax_group:
		tax_group = frappe.db.get_value("Account", {"is_group": 1, "root_type": "Liability",
													"account_type": "Tax", "company": company})

	return tax_group


def make_tax_account(company, account_name, tax_rate):
	tax_group = get_tax_account_group(company)
	if tax_group:
		return frappe.get_doc({
			"doctype": "Account",
			"company": company,
			"parent_account": tax_group,
			"account_name": account_name,
			"is_group": 0,
			"report_type": "Balance Sheet",
			"root_type": "Liability",
			"account_type": "Tax",
			"tax_rate": flt(tax_rate) if tax_rate else None
		}).insert(ignore_permissions=True)


def make_sales_and_purchase_tax_templates(account, template_name=None):
	if not template_name:
		template_name = account.name

	sales_tax_template = {
		"doctype": "Sales Taxes and Charges Template",
		"title": template_name,
		"company": account.company,
		"taxes": [{
			"category": "Valuation and Total",
			"charge_type": "On Net Total",
			"account_head": account.name,
			"description": "{0} @ {1}".format(account.account_name, account.tax_rate),
			"rate": account.tax_rate
		}]
	}

	# Sales
	frappe.get_doc(copy.deepcopy(sales_tax_template)
				   ).insert(ignore_permissions=True)


def create_midwife_tax_template(args):
	account_name = "44566-TVA sur autres biens et services - " + \
		args.get('company_abbr')
	purchase_tax_template = frappe.get_doc({
		"doctype": "Purchase Taxes and Charges Template",
		"title": _("VAT 20% - Included"),
		"company": args.get("company_name"),
		"taxes": [{
			"category": "Total",
			"charge_type": "On Net Total",
			"account_head": account_name,
			"description": _("VAT 20%"),
			"rate": 20,
			"included_in_print_rate": 1
		}]
	}).insert(ignore_permissions=True)

	purchase_tax_template = frappe.get_doc({
		"doctype": "Purchase Taxes and Charges Template",
		"title": _("VAT 10% - Included"),
		"company": args.get("company_name"),
		"taxes": [{
			"category": "Total",
			"charge_type": "On Net Total",
			"account_head": account_name,
			"description": _("VAT 10%"),
			"rate": 10,
			"included_in_print_rate": 1
		}]
	}).insert(ignore_permissions=True)

	purchase_tax_template = frappe.get_doc({
		"doctype": "Purchase Taxes and Charges Template",
		"title": _("VAT 5.5% - Included"),
		"company": args.get("company_name"),
		"taxes": [{
			"category": "Total",
			"charge_type": "On Net Total",
			"account_head": account_name,
			"description": _("VAT 5.5%"),
			"rate": 5.5,
			"included_in_print_rate": 1
		}]
	}).insert(ignore_permissions=True)


def create_items(args):
	for i in xrange(1, 6):
		item = args.get("item_" + str(i))
		if item:
			item_group = _(args.get("item_group_" + str(i)))
			is_sales_item = args.get("is_sales_item_" + str(i))
			is_purchase_item = args.get("is_purchase_item_" + str(i))
			is_stock_item = item_group != _("Services")
			default_warehouse = ""
			if is_stock_item:
				default_warehouse = frappe.db.get_value("Warehouse", filters={
					"warehouse_name": _("Finished Goods") if is_sales_item else _("Stores"),
					"company": args.get("company_name").strip()
				})

			try:
				frappe.get_doc({
					"doctype": "Item",
					"item_code": item,
					"item_name": item,
					"description": item,
					"show_in_website": 1,
					"is_sales_item": is_sales_item,
					"is_purchase_item": is_purchase_item,
					"is_stock_item": is_stock_item and 1 or 0,
					"item_group": item_group,
					"stock_uom": _(args.get("item_uom_" + str(i))),
					"default_warehouse": default_warehouse
				}).insert()

				if args.get("item_img_" + str(i)):
					item_image = args.get("item_img_" + str(i)).split(",")
					if len(item_image) == 3:
						filename, filetype, content = item_image
						fileurl = save_file(
							filename, content, "Item", item, decode=True).file_url
						frappe.db.set_value("Item", item, "image", fileurl)

				if args.get("item_price_" + str(i)):
					item_price = flt(args.get("item_price_" + str(i)))

					if is_sales_item:
						price_list_name = frappe.db.get_value(
							"Price List", {"selling": 1})
						make_item_price(item, price_list_name, item_price)

					if is_purchase_item:
						price_list_name = frappe.db.get_value(
							"Price List", {"buying": 1})
						make_item_price(item, price_list_name, item_price)

			except frappe.NameError:
				pass


def make_item_price(item, price_list_name, item_price):
	frappe.get_doc({
		"doctype": "Item Price",
		"price_list": price_list_name,
		"item_code": item,
		"price_list_rate": item_price
	}).insert()


def correct_midwife_accounts(args):
	hn_account = "7014 - Honoraires hors convention, livre Recettes - " + \
		args.get('company_abbr')
	default_income_account = "7013 - Honoraires conventionnels livre Recettes - " + \
		args.get('company_abbr')
	default_receivable_account = "410 - Clients et Comptes rattachés - " + \
		args.get('company_abbr')
	default_payable_account = "4011 - Fournisseurs - Achats de biens ou de prestations de services - " + \
		args.get('company_abbr')
	round_off_account = "658 - Charges diverses de gestion courante - " + \
		args.get('company_abbr')
	exchange_gain_loss_account = "666 - Pertes de change financières - " + \
		args.get('company_abbr')
	accumulated_depreciation_account = "2815 - Installations techniques, matériel et outillage médical (même ventilation que celle du compte 218) - " + args.get(
		'company_abbr')
	depreciation_expense_account = "68112 - Immobilisations corporelles - " + \
		args.get('company_abbr')
	fee_account = "709 - Honoraires rétrocédés - " + args.get('company_abbr')
	personal_debit_account = "108900 - Compte de l'exploitant - " + \
		args.get('company_abbr')
	meal_expense_deductible_account = "625700 - Frais de repas déductibles - " + args.get('company_abbr')
	meal_expense_non_deductible_account = "108900 - Compte de l'exploitant - " + args.get('company_abbr')
	social_contribution_deductible_account = "6451 - Cotisations à l'URSSAF - " + args.get('company_abbr')
	social_contributions_third_party = "URSSAF"

	if frappe.db.exists('Account', hn_account):
		frappe.db.set_value('Item', "HN", 'income_account', hn_account)

	if frappe.db.exists('Account', default_income_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'default_income_account', default_income_account)

	if frappe.db.exists('Account', default_receivable_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'default_receivable_account', default_receivable_account)

	if frappe.db.exists('Account', default_payable_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'default_payable_account', default_payable_account)

	if frappe.db.exists('Account', round_off_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'round_off_account', round_off_account)
		frappe.db.set_value('Company', args.get(
			'company_name'), 'write_off_account', round_off_account)

	if frappe.db.exists('Account', exchange_gain_loss_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'exchange_gain_loss_account', exchange_gain_loss_account)

	if frappe.db.exists('Account', accumulated_depreciation_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'accumulated_depreciation_account', accumulated_depreciation_account)

	if frappe.db.exists('Account', depreciation_expense_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'depreciation_expense_account', depreciation_expense_account)

	if frappe.db.exists('Account', fee_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'fee_account', fee_account)

	if frappe.db.exists('Account', personal_debit_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'personal_debit_account', personal_debit_account)

	if frappe.db.exists('Account', meal_expense_deductible_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'meal_expense_deductible_account', meal_expense_deductible_account)

	if frappe.db.exists('Account', meal_expense_non_deductible_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'meal_expense_non_deductible_account', meal_expense_non_deductible_account)

	if frappe.db.exists('Account', social_contribution_deductible_account):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'social_contribution_deductible_account', social_contribution_deductible_account)

	if frappe.db.exists('Supplier', social_contributions_third_party):
		frappe.db.set_value('Company', args.get(
			'company_name'), 'social_contributions_third_party', social_contributions_third_party)


def create_customers(args):
	for i in xrange(1, 6):
		customer = args.get("customer_" + str(i))
		if customer:
			try:
				doc = frappe.get_doc({
					"doctype": "Customer",
					"customer_name": customer,
					"customer_type": "Company",
					"customer_group": _("Commercial"),
					"territory": args.get("country"),
					"company": args.get("company_name").strip()
				}).insert()

				if args.get("customer_contact_" + str(i)):
					create_contact(args.get("customer_contact_" + str(i)),
								   "Customer", doc.name)
			except frappe.NameError:
				pass


def create_suppliers(args):
	for i in xrange(1, 6):
		supplier = args.get("supplier_" + str(i))
		if supplier:
			try:
				doc = frappe.get_doc({
					"doctype": "Supplier",
					"supplier_name": supplier,
					"supplier_type": _("Local"),
					"company": args.get("company_name").strip()
				}).insert()

				if args.get("supplier_contact_" + str(i)):
					create_contact(args.get("supplier_contact_" + str(i)),
								   "Supplier", doc.name)
			except frappe.NameError:
				pass


def create_contact(contact, party_type, party):
	"""Create contact based on given contact name"""
	contact = contact.strip().split(" ")

	contact = frappe.get_doc({
		"doctype": "Contact",
		"first_name": contact[0],
		"last_name": len(contact) > 1 and contact[1] or ""
	})
	contact.append('links', dict(link_doctype=party_type, link_name=party))
	contact.insert()


def create_professional_contact_card(args):

	prof_card = frappe.get_doc({
		"doctype": "Professional Information Card",
		"user": args.get("email"),
		"company": args.get("company_name"),
		"full_name": args.get("full_name"),
		"siret_number": args.get("company_siret"),
		"rpps_number": args.get("rpps_number"),
		"phone": args.get("company_phone"),
		"email": args.get("company_email")
	})
	prof_card.insert(ignore_permissions=True)


def create_letter_head(args):
	if args.get("attach_letterhead"):
		frappe.get_doc({
			"doctype": "Letter Head",
			"letter_head_name": _("Standard"),
			"is_default": 1
		}).insert()

		attach_letterhead = args.get("attach_letterhead").split(",")
		if len(attach_letterhead) == 3:
			filename, filetype, content = attach_letterhead
			fileurl = save_file(filename, content, "Letter Head", _(
				"Standard"), decode=True).file_url
			frappe.db.set_value("Letter Head", _(
				"Standard"), "content", "<img src='%s' style='max-width: 100%%;'>" % fileurl)


def create_logo(args):
	if args.get("attach_logo"):
		attach_logo = args.get("attach_logo").split(",")
		if len(attach_logo) == 3:
			filename, filetype, content = attach_logo
			fileurl = save_file(filename, content, "Website Settings", "Website Settings",
								decode=True).file_url
			frappe.db.set_value("Website Settings", "Website Settings", "brand_html",
								"<img src='{0}' style='max-width: 40px; max-height: 25px;'> {1}".format(fileurl, args.get("company_name").strip()))


def create_territories():
	"""create two default territories, one for home country and one named Rest of the World"""
	from frappe.utils.nestedset import get_root_of
	country = frappe.db.get_default("country")
	root_territory = get_root_of("Territory")
	for name in (country, _("Rest Of The World")):
		if name and not frappe.db.exists("Territory", name):
			frappe.get_doc({
				"doctype": "Territory",
				"territory_name": name.replace("'", ""),
				"parent_territory": root_territory,
				"is_group": "No"
			}).insert()


def login_as_first_user(args):
	if args.get("email") and hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.login_as(args.get("email"))


def create_users(args):
	if frappe.session.user == 'Administrator':
		return

	# create employee for self
	emp = frappe.get_doc({
		"doctype": "Employee",
		"employee_name": " ".join(filter(None, [args.get("first_name"), args.get("last_name")])),
		"user_id": frappe.session.user,
		"status": "Active",
		"company": args.get("company_name")
	})
	emp.flags.ignore_mandatory = True
	emp.insert(ignore_permissions=True)

	for i in xrange(1, 5):
		email = args.get("user_email_" + str(i))
		fullname = args.get("user_fullname_" + str(i))
		if email:
			if not fullname:
				fullname = email.split("@")[0]

			parts = fullname.split(" ", 1)

			user = frappe.get_doc({
				"doctype": "User",
				"email": email,
				"first_name": parts[0],
				"last_name": parts[1] if len(parts) > 1 else "",
				"enabled": 1,
				"user_type": "System User"
			})

			# default roles
			user.append_roles("Projects User", "Stock User", "Support Team")

			if args.get("user_sales_" + str(i)):
				user.append_roles(
					"Sales User", "Sales Manager", "Accounts User")
			if args.get("user_purchaser_" + str(i)):
				user.append_roles(
					"Purchase User", "Purchase Manager", "Accounts User")
			if args.get("user_accountant_" + str(i)):
				user.append_roles("Accounts Manager", "Accounts User")

			user.flags.delay_emails = True

			if not frappe.db.get_value("User", email):
				user.insert(ignore_permissions=True)

				# create employee
				emp = frappe.get_doc({
					"doctype": "Employee",
					"employee_name": fullname,
					"user_id": email,
					"status": "Active",
					"company": args.get("company_name")
				})
				emp.flags.ignore_mandatory = True
				emp.insert(ignore_permissions=True)


def web_portal_settings():
	frappe.reload_doctype("Portal Settings")

	items = frappe.get_all("Portal Menu Item", fields=[
						   'name', 'title', 'route', 'enabled'])

	for item in items:
		if item.route == "/appointment" or item.route == "/my-appointments":
			pass
		else:
			frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

	frappe.db.commit()


def make_web_page(args):
	# home page
	homepage = frappe.get_doc('Homepage', 'Homepage')
	homepage.company = args.get('company_name').strip()
	homepage.tag_line = args.get('company_name').strip()
	homepage.description = "Connectez-vous pour prendre rendez-vous"
	homepage.save()

	website_settings = frappe.get_doc(
		'Website Settings', 'Website Settings')
	website_settings.home_page = 'home'
	website_settings.save()


def disable_signup():
	frappe.db.set_value("Website Settings",
						"Website Settings", "disable_signup", 1)
	frappe.db.commit()


def disable_guest_access():
	frappe.db.set_value("Shopping Cart Settings", "Shopping Cart Settings", "enabled", 0)

	frappe.db.set_value("Role", "Guest", "desk_access", 0)

	frappe.db.commit()


def set_default_print_formats():
	print_formats = ["Patient Folder", "Prenatal Interview Folder", "Perineum Rehabilitation Folder", "Gynecology Folder", "Pregnancy Folder", "Postnatal Consultation",
					 "Birth Preparation Consultation", "Perineum Rehabilitation Consultation", "Free Consultation", "Early Postnatal Consultation", "Gynecological Consultation", "Pregnancy Consultation", "Drug Prescription"]

	for print_format in print_formats:
		make_default(print_format)


def add_terms_and_conditions():
	terms = frappe.get_doc({
		"doctype": "Terms and Conditions",
		"title": "Termes et Conditions Standard",
		"terms": "Membre d'une société de gestion agréée, les règlements par chèques sont acceptés."
	})
	try:
		terms.insert(ignore_permissions=True)
		frappe.db.commit()
	except:
		pass


def create_item_groups(args):
	frappe.db.set_value("Item Group", _("Purchases"), "default_expense_account", "602 - Achats stockés - Autres approvisionnements - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Rental Expenses"), "default_expense_account", "613 - Locations - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Furniture and Equipment Rental"), "default_expense_account", "613 - Locations - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Maintenance and Repair"), "default_expense_account", "615 - Entretiens et réparations - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Temporary Staff"), "default_expense_account", "621 - Personnel extérieur à l'entreprise - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Small Equipment"), "default_expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Heating, Water, Gaz, Electricity"), "default_expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Fees without Retrocession"), "default_expense_account", "622 - Rémunérations d'intermédiaires et honoraires - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Insurance Premium"), "default_expense_account", "616 - Primes d'assurance - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Vehicule Expenses"), "default_expense_account", "625200 - Frais de Véhicule - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Other Travel Related Costs"), "default_expense_account", "625100 - Voyages et déplacements - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Personal Social Security Contributions"), "default_expense_account", "6451 - Cotisations à l'URSSAF - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Reception and Representation Expenses"), "default_expense_account", "625720 - Frais de réceptions déductibles - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Office Supplies, Documentation, Post Office"), "default_expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Deeds and Litigation Costs"), "default_expense_account", "622 - Rémunérations d'intermédiaires et honoraires - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Professional Organizations Contributions"), "default_expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Miscellaneous Management Expenses"), "default_expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item Group", _("Financial Expenses"), "default_expense_account", "668 - Autres charges financières - " + args.get('company_abbr'))
	frappe.db.commit()


def create_purchase_items(args):
	frappe.db.set_value("Item", _('Exam Sheets'), "expense_account", "602 - Achats stockés - Autres approvisionnements - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Medical Equipment'), "expense_account", "602 - Achats stockés - Autres approvisionnements - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Disposable Equipment'), "expense_account", "602 - Achats stockés - Autres approvisionnements - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Rent'), "expense_account", "613 - Locations - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Rental Expense'), "expense_account", "614 - Charges locatives et de copropriété - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Collaboration Fee'), "expense_account", "613 - Locations - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Finance Lease Rent'), "expense_account", "6125 - Crédit-bail immobilier - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Duty paid to an Hospital or Clinic'), "expense_account", "613 - Locations - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Maintenance and Repair Expenses'), "expense_account", "615 - Entretiens et réparations - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Laundering Expenses'), "expense_account", "615 - Entretiens et réparations - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Temporary Staff'), "expense_account", "621 - Personnel extérieur à l'entreprise - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Small Material'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Software'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Office Furniture'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Clothing Expenses'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Heating'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Water'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Gaz'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Electricity'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Fees paid to professionals other than peers'), "expense_account", "622 - Rémunérations d'intermédiaires et honoraires - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Remuneration for complementary services'), "expense_account", "622 - Rémunérations d'intermédiaires et honoraires - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Deductible Premium'), "expense_account", "616 - Primes d'assurance - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Non Deductible Premium'), "expense_account", "616 - Primes d'assurance - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Vehicule Expenses'), "expense_account", "625200 - Frais de Véhicule - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Travel Expenses'), "expense_account", "625100 - Voyages et déplacements - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Mandatory Personal Social Security Contributions'), "expense_account", "6451 - Cotisations à l'URSSAF - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Optional Personal Social Security Contributions'), "expense_account", "645 - Charges de sécurité sociale et de prévoyance - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Reception and Representation Expenses'), "expense_account", "625100 - Voyages et déplacements - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Consumable Supplies'), "expense_account", "606 - Achats non stockés de matières et founitures - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Professional Magazine'), "expense_account", "6181 - Documentation générale - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Post Office'), "expense_account", "626 - Frais postaux et de télécommunications - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Deeds and Litigation Costs'), "expense_account", "622 - Rémunérations d'intermédiaires et honoraires - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Certified Management Association'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('College of Midwifes'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Midwifes Union'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Regional Medical Professionals Union'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Bank Account Operating Expenses'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Waiting Room Magazines'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Phone Desk Expenses'), "expense_account", "628 - Divers - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Interests and Professional Loan'), "expense_account", "668 - Autres charges financières - " + args.get('company_abbr'))
	frappe.db.set_value("Item", _('Agios'), "expense_account", "668 - Autres charges financières - " + args.get('company_abbr'))
	frappe.db.commit()


def setup_asset_categories_accounts(args):
	categories = [{'name': _('Professional Premises'), 'faa': '2131 - Bâtiments - ','dea': '68112 - Immobilisations corporelles - '}, {'name':_('Repairs'), 'faa': '2135 - Installations G\u00e9n\u00e9rales, agencements, am\u00e9nagements des constructions - ','dea': '68112 - Immobilisations corporelles - '},
	{'name':_('Tools'), 'faa': '2155 - Outillage - ','dea': '68112 - Immobilisations corporelles - '}, {'name':_('Facilities'), 'faa': '2181 - Installations générales, agencements, aménagements divers - ','dea': '68112 - Immobilisations corporelles - '}, {'name':_('Furniture'), 'faa': '2184 - Mobilier - ','dea': '68112 - Immobilisations corporelles - '},
	{'name':_('Computer'), 'faa': '2183 - Matériel de bureau et matériel informatique - ','dea': '68112 - Immobilisations corporelles - '}, {'name':_('Medical Material'), 'faa': '2154 - Matériel médical - ','dea': '68112 - Immobilisations corporelles - '},
	{'name':_('Car'), 'faa': '208 - Autres immobilisations incorporelles - ','dea': '68111 - Immobilisations incorporelles - '}]
	for category in categories:

		asset_category = frappe.get_doc("Asset Category", category['name'])
		try:
			asset_category.append('accounts', {'company_name': args.get('company_name').strip(), 'fixed_asset_account': category['faa'] + args.get('company_abbr'),'accumulated_depreciation_account': category['faa'] + args.get('company_abbr'),'depreciation_expense_account': category['dea'] + args.get('company_abbr')})
			asset_category.save(ignore_permissions=True)
		except Exception as e:
			pass

def social_security_account(args):
	ss = frappe.get_doc("Supplier Type", _('Social Security'))
	ss.append("accounts", {
		"company": args.company,
		"account": "431 - Sécurité sociale - " + args.get('company_abbr')
	})

	ss.save(ignore_permissions=True)
