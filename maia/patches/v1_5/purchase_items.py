# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


def execute():
	language = frappe.get_single("System Settings").language
	frappe.local.lang = language

	records = [
	{'doctype': 'Item Group', 'item_group_name': _('Vehicule Expenses'), 'is_group': 0, 'parent_item_group': _('Buying') },
	{'uom_name': _('Month'), 'doctype': 'UOM', 'name': _('Minute')},
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
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError, e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

	frappe.rename_doc("Item Group", "Frais d'Actes et de Contentieux", "Actes et Contentieux")
	frappe.rename_doc("Item Group", "Frais de Réception, de Représentation, de Congrès", "Frais de Réceptions, de Représentations, de Congrès")


	from maia.setup.setup_wizard.install_fixtures import purchase_items
	purchase_items()

	from maia.setup.setup_wizard.setup_wizard import create_purchase_items
	companies = frappe.get_all("Company")
	abbr = frappe.get_value("Company", companies[0].name, "abbr")

	frappe.db.set_value("Item Group", _("Vehicule Expenses"), "default_expense_account", "625200-Frais de Véhicule - " + abbr)
	frappe.db.commit()

	create_purchase_items({"company_abbr": abbr})
