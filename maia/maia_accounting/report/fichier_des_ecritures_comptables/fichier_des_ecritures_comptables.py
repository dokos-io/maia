# Copyright (c) 2013, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import format_datetime
from frappe import _
import re
from maia.maia_accounting.utils import get_fiscal_year

def execute(filters=None):
	account_details = {}
	for acc in frappe.db.sql("""select name from `tabAccounting Item`""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters)

	return columns, res


def validate_filters(filters, account_details):
	if not filters.get('practitioner'):
		frappe.throw(_('Practitioner is mandatory'))

	if not filters.get('fiscal_year'):
		frappe.throw(_('Fiscal Year is mandatory'))


def set_account_currency(filters):

	filters["company_currency"] = "EUR"

	return filters


def get_columns(filters):
	columns = [
		"JournalCode" + "::90", "JournalLib" + "::90",
		"EcritureNum" + ":Dynamic Link:90", "EcritureDate" + "::90",
		"CompteNum" + ":Link/Accounting Item:100", "CompteLib" + ":Link/Accounting Item:200",
		"CompAuxNum" + "::90", "CompAuxLib" + "::90",
		"PieceRef" + "::90", "PieceDate" + "::90",
		"EcritureLib" + "::90", "Debit" + "::90", "Credit" + "::90",
		"EcritureLet" + "::90", "DateLet" +
		"::90", "ValidDate" + "::90",
		"Montantdevise" + "::90", "Idevise" + "::90"
	]

	return columns


def get_result(filters):
	gl_entries = get_gl_entries(filters)
	result = get_result_as_list(gl_entries, filters)

	return result


def get_gl_entries(filters):

	gl_entries = frappe.db.sql("""
		select
			gl.posting_date as GlPostDate, gl.name as GlName, gl.accounting_item, gl.posting_date,
			gl.accounting_journal, gl.party, gl.link_docname,
			sum(gl.debit) as debit, sum(gl.credit) as credit,
			gl.reference_type, gl.reference_name, gl.currency,
			rev.name as RevName, rev.label as RevTitle, rev.transaction_date as RevPostDate,
			rev.party as RevParty, rev.patient as RevPatient,
			exp.name as ExpName, exp.label as ExpTitle, exp.transaction_date as ExpPostDate,
			exp.party as ExpParty,
			pay.name as PayName, pay.payment_date as PayPostDate, pay.title as PayTitle,
			pat.patient_name, pat.name as patName,
			par.name as parName
 
		from `tabGeneral Ledger Entry` gl
			left join `tabRevenue` rev on gl.reference_name = rev.name
			left join `tabExpense` exp on gl.reference_name = exp.name
			left join `tabPayment` pay on gl.reference_name = pay.name
			left join `tabPatient Record` pat on rev.patient = pat.name
			left join `tabParty` par on rev.party = par.name or exp.party = par.name
			
		where gl.practitioner=%(practitioner)s
		{conditions}
		group by gl.name
		order by GlPostDate, reference_name""".format(conditions=get_conditions(filters)), filters, as_dict=1)

	return gl_entries

def get_conditions(filters):
	conditions = []

	if filters.get("fiscal_year"):
		fy = get_fiscal_year(fiscal_year=filters.get("fiscal_year"), as_dict=1)
		conditions.append("posting_date>='{0}' and posting_date<='{1}'".format(fy.year_start_date, fy.year_end_date))

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("General Ledger Entry")

	if match_conditions:
		conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_result_as_list(data, filters):
	result = []

	company_currency = "EUR"
	accounts = frappe.get_all("Accounting Item", fields=["name", "accounting_number"])

	for d in data:
		JournalCode = d.get("accounting_journal")

		EcritureNum = d.get("GlName")

		EcritureDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")

		account_number = [account.accounting_number for account in accounts if account.name == d.get("accounting_item")]
		if account_number[0] is not None:
			CompteNum = account_number[0]
		else:
			frappe.throw(_("Account numbers are not available for all accounts.<br> Please setup your Chart of Accounts correctly."))

		if d.get("patName"):
			CompAuxNum = d.get("patName")
			CompAuxLib = d.get("patient_name")

		elif d.get("parName"):
			CompAuxNum = d.get("parName")
			CompAuxLib = d.get("parName")

		elif d.get("party"):
			CompAuxNum = d.get("party")
			CompAuxLib = d.get("party")

		else:
			CompAuxNum = ""
			CompAuxLib = ""

		ValidDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")
		PieceRef = d.get("reference_name")

		# EcritureLib is the reference title unless it is an opening entry
		if d.get("is_opening") == "Yes":
			EcritureLib = _("Opening Entry Journal")
		if d.get("reference_type") == "Revenue":
			EcritureLib = d.get("RevTitle")
		elif d.get("reference_type") == "Expense":
			EcritureLib = d.get("ExpTitle")
		elif d.get("reference_type") == "Payment":
			EcritureLib = d.get("PayTitle")
		else:
			EcritureLib = d.get("reference_name")

		PieceDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")

		debit = '{:.2f}'.format(d.get("debit")).replace(".", ",")

		credit = '{:.2f}'.format(d.get("credit")).replace(".", ",")

		EcritureLet = d.get("link_docname") if d.get("link_docname") != d.get("reference_name") else None
		DateLet = format_datetime(d.get("GlPostDate"), "yyyyMMdd") if EcritureLet else None

		Montantdevise = '{:.2f}'.format(d.get("debit")).replace(".", ",") if d.get("debit") != 0 else '{:.2f}'.format(d.get("credit")).replace(".", ",")

		row = [JournalCode, JournalCode, EcritureNum, EcritureDate, CompteNum, d.get("accounting_item"), CompAuxNum, CompAuxLib,
				PieceRef, PieceDate, EcritureLib, debit, credit, EcritureLet, DateLet, ValidDate, Montantdevise, "EUR"]

		result.append(row)

	return result

