from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Billing"),
			"items": [
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"description": _("Bills raised to Customers.")
				},
				{
					"type": "doctype",
					"name": "Purchase Invoice",
					"description": _("Bills raised by Suppliers.")
				},
				{
					"type": "doctype",
					"name": "Payment Entry",
					"description": _("Bank/Cash transactions against party or for internal transfer")
				}
			]

		},
		{
			"label": _("Day-to-day Operations"),
			"items": [
				{
					"type": "doctype",
					"name": "Meal Expense",
					"doctype": "Meal Expense"
				},
				{
					"type": "doctype",
					"name": "Journal Entry",
					"description": _("Accounting journal entries.")
				},
				{
					"type": "doctype",
					"name": "Personal Debit",
					"doctype": "Personal Debit"
				},
				{
					"type": "doctype",
					"name": "Fee Retrocession",
					"doctype": "Fee Retrocession"
				},
				{
					"type": "doctype",
					"name": "Social Contribution",
					"label": _("Social Contributions"),
					"doctype": "Social Contribution"
				}
			]
		},
		{
			"label": _("Ledgers and P/L Statements"),
			"items": [
				{
					"type": "report",
					"name": "Sales Register",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase Register",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name":"General Ledger",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Profit and Loss Statement",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Balance Sheet",
					"doctype": "GL Entry",
					"is_query_report": True
				}
			]
		},
				{
					"label": _("Reports"),
					"items": [
						{
							"type": "report",
							"name": "Sales Invoice Trends",
							"is_query_report": True,
							"doctype": "Sales Invoice"
						},
						{
							"type": "report",
							"name": "Cash Flow",
							"doctype": "GL Entry",
							"is_query_report": True
						},
						{
							"type": "report",
							"name": "Accounts Receivable Summary",
							"doctype": "Sales Invoice",
							"is_query_report": True
						},
						{
							"type": "report",
							"name": "Accounts Payable Summary",
							"doctype": "Purchase Invoice",
							"is_query_report": True
						},
						{
							"type": "report",
							"name": "Midwife Replacement Report",
							"doctype": "GL Entry",
							"is_query_report": True
						}
					]
				},
		{
			"label": _("Banking Operations"),
			"items": [
				{
					"type": "doctype",
					"name": "Cash Deposit",
					"doctype": "Cash Deposit"
				},
				{
					"type": "doctype",
					"label": _("Update Bank Transaction Dates"),
					"name": "Bank Reconciliation",
					"description": _("Update bank payment dates with journals.")
				},
				{
					"type": "report",
					"name": "Bank Reconciliation Statement",
					"is_query_report": True,
					"doctype": "Journal Entry"
				}
			]
		},
		{
			"label": _("Depreciations"),
			"items": [
				{
					"type": "doctype",
					"name": "Asset",
				},
				{
					"type": "doctype",
					"name": "Asset Category",
				},
				{
					"type": "report",
					"name": "Asset Depreciation Ledger",
					"doctype": "Asset",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Asset Depreciations and Balances",
					"doctype": "Asset",
					"is_query_report": True,
				}
			]
		},
		{
			"label": _("Setup"),
			"icon": "fa fa-cog",
			"items": [
				{
					"type": "doctype",
					"name":"Mode of Payment",
					"description": _("e.g. Bank, Cash, Credit Card")
				},
				{
					"type": "doctype",
					"name":"Terms and Conditions",
					"label": _("Terms and Conditions Template"),
					"description": _("Template of terms or contract.")
				},
				{
					"type": "doctype",
					"name": "Account",
					"icon": "fa fa-sitemap",
					"label": _("Chart of Accounts"),
					"route": "Tree/Account",
					"description": _("Tree of financial accounts."),
				},
				{
					"type": "doctype",
					"name": "Company",
					"description": _("Company (not Customer or Supplier) master.")
				},
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Customer database.")
				},
				{
					"type": "doctype",
					"name": "Supplier",
					"description": _("Supplier database.")
				},
				{
					"type": "doctype",
					"name": "Item",
				}
			]
		}
	]
