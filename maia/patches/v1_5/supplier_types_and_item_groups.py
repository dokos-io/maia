# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


def execute():

	# Supplier Types
	frappe.rename_doc("Supplier Type", "Fournitures et Pharmacie", "Fournitures")

	try:
		doc = frappe.get_doc("Supplier Type", "Travaux, Fournitures, Services Extérieurs")
		doc.delete()
	except Exception as e:
		print(e)
	try:
		doc = frappe.get_doc("Supplier Type", "Locale")
		doc.delete()
	except Exception as e:
		print(e)

	doc = frappe.new_doc("Supplier Type")
	doc.supplier_type = "Supermarché"
	try:
		doc.save()
	except Exception as e:
		print(e)

	doc = frappe.new_doc("Supplier Type")
	doc.supplier_type = "Restaurant"
	try:
		doc.save()
	except Exception as e:
		print(e)

	frappe.db.commit()

	# Item Groups Deletion
	try:
		doc = frappe.get_doc("Item Group", "Consommable")
		doc.delete()
	except Exception as e:
		print(e)

	try:
		doc = frappe.get_doc("Item Group", "Sous-Assemblages")
		doc.delete()
	except Exception as e:
		print(e)

	try:
		doc = frappe.get_doc("Item Group", "Services")
		doc.delete()
	except Exception as e:
		print(e)

	try:
		doc = frappe.get_doc("Item Group", "Matières Premières")
		doc.delete()
	except Exception as e:
		print(e)

	try:
		doc = frappe.get_doc("Item Group", "Produits")
		doc.delete()
	except Exception as e:
		print(e)

	frappe.db.commit()


	#Item Groups Creation
	print("Item Groups Creation")

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Achat"
	doc.parent_item_group = "Tous les Groupes d'Articles"
	doc.is_group = 1
	try:
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		print(e)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Vente"
	doc.parent_item_group = "Tous les Groupes d'Articles"
	doc.is_group = 1
	try:
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		print(e)

	doc = frappe.get_doc("Item Group", "Codifications")
	doc.parent_item_group = "Vente"
	try:
		doc.save()
		frappe.db.commit()
	except Exception as e:
		print(e)

	print("Fetch Company and Modify CoA")
	companies = frappe.get_all("Company")
	for company in companies:
		abbr = frappe.db.get_value("Company", company.name, "abbr")

		try:
			existing_account = frappe.get_doc(
				"Account", "602-Achats stockés - Autres approvisionnements - " + abbr)

		except:
			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "60-Achats (sauf 603) - " + abbr,
				"account_name": "602-Achats stockés - Autres approvisionnements",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			frappe.db.commit()


			account = frappe.get_doc("Account", "6132-Locations immobilières - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6135-Locations mobilières - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6136-Malis sur emballages - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "613-Locations - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "61-Services extérieurs - " + abbr,
				"account_name": "613-Locations",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6152-Entretiens et réparations - sur biens immobiliers - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6155-Entretiens et réparations - sur biens mobiliers - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6156-Maintenance - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "615-Entretiens et réparations - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "61-Services extérieurs - " + abbr,
				"account_name": "615-Entretiens et réparations",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6211-Personnel intérimaire - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6214-Personnel détaché ou prêté à l'entreprise - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "621-Personnel extérieur à l'entreprise - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "62-Autres services extérieurs - " + abbr,
				"account_name": "621-Personnel extérieur à l'entreprise",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6068-Autres matières et fournitures - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6064-Fournitures administratives - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6063-Fournitures d'entretien et de petit équipement - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6061-Fournitures non stockables (eau, énergie...) - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "606-Achats non stockés de matières et founitures - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "60-Achats (sauf 603) - " + abbr,
				"account_name": "606-Achats non stockés de matières et founitures",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6228-Divers - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6227-Frais d'actes et de contentieux - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6226-Honoraires - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "622-Rémunérations d'intermédiaires et honoraires - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "62-Autres services extérieurs - " + abbr,
				"account_name": "622-Rémunérations d'intermédiaires et honoraires",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6165-Insolvabilité clients - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6164-Risques d'exploitation - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6162-Assurance obligatoire dommage construction - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6161-Multirisques - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "61638-Assurance-transport - sur autres biens - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "61637-Assurance-transport - sur ventes - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "61636-Assurance-transport - sur achats - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6163-Assurance-transport - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "616-Primes d'assurance - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "61-Services extérieurs - " + abbr,
				"account_name": "616-Primes d'assurance",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6257-Réceptions - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6255-Frais de déménagement - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6251-Voyages et déplacements - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "625-Déplacements, missions et réceptions - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "62-Autres services extérieurs - " + abbr,
				"account_name": "625-Déplacements, missions et réceptions",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6451-Cotisations à l'URSSAF - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6452-Cotisations aux mutuelles - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6453-Cotisations aux caisses de retraites - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6454-Cotisations aux ASSEDIC - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "645-Charges de sécurité sociale et de prévoyance - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "64-Charges de personnel - " + abbr,
				"account_name": "645-Charges de sécurité sociale et de prévoyance",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)

			account = frappe.get_doc("Account", "6281-Concours divers (cotisations...) - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "6284-Frais de recrutement de personnel - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			account = frappe.get_doc("Account", "628-Divers - " + abbr)
			try:
				account.delete()
			except Exception as e:
				print(e)

			frappe.db.commit()

			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "62-Autres services extérieurs - " + abbr,
				"account_name": "628-Divers",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)



	print("Make item groups")
	abbr = frappe.db.get_value("Company", companies[0].name, "abbr")


	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Achats"
	doc.parent_item_group = "Achat"
	doc.default_expense_account = "602-Achats stockés - Autres approvisionnements - " + abbr
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Loyer et Charges Locatives"
	doc.default_expense_account = "613-Locations - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Location de Matériel et de Mobilier"
	doc.default_expense_account = "613-Locations - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Entretien et Réparations"
	doc.default_expense_account = "615-Entretiens et réparations - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Personnel Intérimaire"
	doc.default_expense_account = "621-Personnel extérieur à l'entreprise - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Petit Outillage"
	doc.default_expense_account = "606-Achats non stockés de matières et founitures - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Chauffage, Eau, Gaz, Electricité"
	doc.default_expense_account = "606-Achats non stockés de matières et founitures - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Honoraires ne constituant pas de Rétrocession"
	doc.default_expense_account = "622-Rémunérations d'intermédiaires et honoraires - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Primes d'Assurance"
	doc.default_expense_account = "616-Primes d'assurance - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Autres Frais de Déplacement"
	doc.default_expense_account = "625-Déplacements, missions et réceptions - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Charges Sociales Personnelles"
	doc.default_expense_account = "645-Charges de sécurité sociale et de prévoyance - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Frais de Réception, de Représentation, de Congrès"
	doc.default_expense_account = "625-Déplacements, missions et réceptions - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Fournitures de Bureau, Documentation, PTT"
	doc.default_expense_account = "606-Achats non stockés de matières et founitures - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Frais d'Actes et de Contentieux"
	doc.default_expense_account = "622-Rémunérations d'intermédiaires et honoraires - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Cotisations Syndicales et Professionnelles"
	doc.default_expense_account = "628-Divers - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Autres Frais Divers de Gestion"
	doc.default_expense_account = "628-Divers - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	doc = frappe.new_doc("Item Group")
	doc.item_group_name = "Frais Financiers"
	doc.default_expense_account = "668-Autres charges financières - " + abbr
	doc.parent_item_group = "Achat"
	doc.insert(ignore_permissions=True)

	frappe.db.commit()
