# coding=utf-8
# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.doctype.desktop_icon.desktop_icon import set_hidden_list
from frappe.printing.doctype.print_format.print_format import make_default

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


def create_midwife_tax_template(args):
	account_name = "44566 - TVA sur autres biens et services - " + args.get('company_abbr')
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

def social_security_account(args):
	ss = frappe.get_doc("Supplier Type", _('Social Security'))
	ss.append("accounts", {
		"company": args.get('company_name'),
		"account": "431 - Sécurité sociale - " + args.get('company_abbr')
	})

	ss.save(ignore_permissions=True)

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

def set_mode_of_payment_account(args):
	list_of_payment_modes = frappe.get_all('Mode of Payment', filters={'type': 'Bank'}, fields=['name'])
	if args.get("bank_account"):
		default_bank_account = "512100 - " + args.get("bank_account") + " - " + args.get('company_abbr')
	else:
		default_bank_account = "5121 - Comptes en monnaie nationale - " + args.get('company_abbr')
	company_name = args.get('company_name').strip()
	for list_of_payment_mode in list_of_payment_modes:
		mode_of_payment = frappe.get_doc(
			'Mode of Payment', list_of_payment_mode.name)
		mode_of_payment.append('accounts', {
			'company': company_name,
			'default_account': default_bank_account
		})
		mode_of_payment.save(ignore_permissions=True)

def set_initial_icons_list(args):
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
	frappe.db.commit()

def correct_midwife_accounts(args):
	hn_account = "7014 - Honoraires hors convention, livre Recettes - " + args.get('company_abbr')
	default_income_account = "7013 - Honoraires conventionnels livre Recettes - " + args.get('company_abbr')
	default_receivable_account = "410 - Clients et Comptes rattachés - " + args.get('company_abbr')
	default_payable_account = "4011 - Fournisseurs - Achats de biens ou de prestations de services - " + args.get('company_abbr')
	round_off_account = "658 - Charges diverses de gestion courante - " + args.get('company_abbr')
	exchange_gain_loss_account = "666 - Pertes de change financières - " + args.get('company_abbr')
	accumulated_depreciation_account = "2815 - Installations techniques, matériel et outillage médical (même ventilation que celle du compte 218) - " + args.get('company_abbr')
	depreciation_expense_account = "68112 - Immobilisations corporelles - " + args.get('company_abbr')
	fee_account = "709 - Honoraires rétrocédés - " + args.get('company_abbr')
	personal_debit_account = "108900 - Compte de l'exploitant - " + args.get('company_abbr')
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

def set_default_print_formats():
	print_formats = ["Patient Folder", "Prenatal Interview Folder", "Perineum Rehabilitation Folder", "Gynecology Folder", "Pregnancy Folder", "Postnatal Consultation",
					 "Birth Preparation Consultation", "Perineum Rehabilitation Consultation", "Free Consultation", "Early Postnatal Consultation", "Gynecological Consultation", "Pregnancy Consultation", "Drug Prescription", "Facture Maia"]

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

def disable_signup():
	frappe.db.set_value("Website Settings", "Website Settings", "disable_signup", 1)
	frappe.db.commit()

def disable_guest_access():
	frappe.db.set_value("Shopping Cart Settings", "Shopping Cart Settings", "enabled", 0)

	frappe.db.set_value("Role", "Guest", "desk_access", 0)

	frappe.db.commit()
