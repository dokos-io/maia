# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


def execute():
	language = frappe.get_single("System Settings").language
	frappe.local.lang = language

	records = [
	{'doctype': 'Asset Category', 'asset_category_name': _('Professional Premises'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 20,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Repairs'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 10,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Tools'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 5,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Facilities'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 5,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Furniture'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 5,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Computer'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 3,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Medical Material'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 5,'frequency_of_depreciation': 12},
	{'doctype': 'Asset Category', 'asset_category_name': _('Car'),'depreciation_method': 'Straight Line', 'total_number_of_depreciations': 5,'frequency_of_depreciation': 12}
	]

	from frappe.modules import scrub
	for r in records:
		print(r)
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.flags.ignore_mandatory = True
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

	companies = frappe.get_all("Company")

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")
		try:
			existing_account = frappe.get_doc("Account", "2135-Installations G\u00e9n\u00e9rales, agencements, am\u00e9nagements des constructions - " + abbr)

		except:
			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Asset",
				"company": company.name,
				"parent_account": "213-Constructions - " + abbr,
				"account_name": "2135-Installations G\u00e9n\u00e9rales, agencements, am\u00e9nagements des constructions",
				"account_type": "Fixed Asset",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			try:
				existing_account = frappe.get_doc("Account", "2155-Outillage - " + abbr)

			except:
				child_account = frappe.get_doc({
					"doctype": "Account",
					"root_type": "Asset",
					"company": company.name,
					"parent_account": "215-Installations techniques, mat\u00e9riel et outillage - " + abbr,
					"account_name": "2155-Outillage",
					"account_type": "Fixed Asset",
					"is_group": 0})

				child_account.insert(ignore_permissions=True)

	frappe.db.commit()

	categories = [{'name': _('Professional Premises'), 'faa': '2131-Bâtiments - ','dea': '68112-Immobilisations corporelles - '}, {'name':_('Repairs'), 'faa': '2135-Installations G\u00e9n\u00e9rales, agencements, am\u00e9nagements des constructions - ','dea': '68112-Immobilisations corporelles - '},
	{'name':_('Tools'), 'faa': '2155-Outillage - ','dea': '68112-Immobilisations corporelles - '}, {'name':_('Facilities'), 'faa': '2181-Installations générales, agencements, aménagements divers - ','dea': '68112-Immobilisations corporelles - '}, {'name':_('Furniture'), 'faa': '2184-Mobilier - ','dea': '68112-Immobilisations corporelles - '},
	{'name':_('Computer'), 'faa': '2183-Matériel de bureau et matériel informatique - ','dea': '68112-Immobilisations corporelles - '}, {'name':_('Medical Material'), 'faa': '2154-Matériel médical - ','dea': '68112-Immobilisations corporelles - '},
	{'name':_('Car'), 'faa': '208-Autres immobilisations incorporelles - ','dea': '68111-Immobilisations incorporelles - '}]
	for category in categories:
		for company in companies:
			abbr = frappe.get_value("Company", company.name, "abbr")

			asset_category = frappe.get_doc("Asset Category", category['name'])
			asset_category.append('accounts', {'company_name': company.name, 'fixed_asset_account': category['faa'] + abbr,'accumulated_depreciation_account': category['faa'] + abbr,'depreciation_expense_account': category['dea'] + abbr})
			asset_category.save(ignore_permissions=True)
