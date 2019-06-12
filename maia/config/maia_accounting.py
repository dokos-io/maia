from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Daily Operations"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Revenue",
					"label": _("Revenue"),
					"description": _("Revenue"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Expense",
					"label": _("Expense"),
					"description": _("Expense"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Miscellaneous Operation",
					"label": _("Miscellaneous Operation"),
					"description": _("Miscellaneous Operation"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Payment",
					"label": _("Payment"),
					"description": _("Payments"),
					"onboard": 1
				}
			]
		},
		{
			"label": _("Assets"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Maia Asset",
					"label": _("Asset"),
					"description": _("Assets"),
					"onboard": 1
				}
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"name": "Maia General Ledger",
					"label": _("General Ledger"),
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Maia Profit and Loss Statement",
					"label": _("Profit and Loss Statement"),
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Bank Balance",
					"label": _("Bank Balance"),
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Declaration 2035",
					"label": _("Déclaration 2035"),
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Fichier des Ecritures Comptables",
					"label": _("Fichier des écritures comptables"),
					"is_query_report": True,
				}
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Party",
					"label": _("Party"),
					"description": _("Parties"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Accounting Item",
					"label": _("Accounting Item"),
					"description": _("Accounting Items"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Payment Method",
					"label": _("Payment Methods"),
					"description": _("Payment Methods")
				},
				{
					"type": "doctype",
					"name": "Bank Statement Balance",
					"label": _("Bank Statement Balance"),
					"description": _("Bank Statement Balance"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Maia Payment Method",
					"label": _("Payment Method"),
					"description": _("Payment Methods"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Maia Bank Account",
					"label": _("Bank Account"),
					"description": _("Bank Accounts"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Maia Fiscal Year",
					"label": _("Fiscal Year"),
					"description": _("Fiscal Years"),
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Meal Expense Deduction",
					"label": _("Meal Expense Deduction"),
					"description": _("Meal Expense Deduction")
				}
			]
		},
	]
