# Copyright (c) 2013, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import os
from frappe.utils import flt
from maia.maia_accounting.utils import get_fiscal_year

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_data(filters):
	data = []
	path = os.path.join(frappe.get_module_path('maia_accounting'), "report", "declaration_2035", "2035.json")
	cerfa = frappe.get_file_json(path)
	
	for cat in cerfa:
		data.append({
			"label": cat,
			"indent": 0
		})
		for item in cerfa[cat]:
			data.append({
				"line": cerfa[cat][item]["line"],
				"label": item,
				"cell": cerfa[cat][item]["cell"],
				"indent": 1,
				"amount": 0,
				"total": cerfa[cat][item]["total"] if "total" in cerfa[cat][item] else None,
				"calculation": cerfa[cat][item]["calculation"] if "calculation" in cerfa[cat][item] else None
			})

			for sub in cerfa[cat][item]:
				if isinstance(cerfa[cat][item][sub], dict):
					data.append({
						"line": cerfa[cat][item][sub]["line"],
						"label": sub,
						"cell": cerfa[cat][item][sub]["cell"],
						"indent": 2,
						"amount": 0,
						"total": cerfa[cat][item]["total"] if "total" in cerfa[cat][item] else None,
						"calculation": cerfa[cat][item]["calculation"] if "calculation" in cerfa[cat][item] else None
					})

		data.append({})

	data = calculate_amounts(filters, data)

	data = calculate_totals(data)

	return data

def calculate_amounts(filters, data):
	gl_entries = get_gl_entries(filters)

	for entry in gl_entries:
		if entry.line_2035 and entry.code_2035:
			for d in data:
				if "line" in d and "cell" in d:
					if d["line"] == entry.line_2035 and d["cell"] == entry.code_2035:
						d["amount"] = flt(d["amount"]) + flt(entry.credit) - flt(entry.debit)

	return data

def calculate_totals(data):
	for d in data:
		if "amount" in d:
			d["amount"] = abs(d["amount"])

		if "total" in d and d["total"]:
			for l in d["total"]:
				iteration_data = data.copy()
				for x in iteration_data:
					if "line" in x and x["line"] == l:
						d["amount"] += flt(x["amount"])

		if "calculation" in d and d["calculation"]:
			value = 0
			operator = "plus"
			for i, c in enumerate(d["calculation"]):
				if c == "plus":
					operator = "plus"
				elif c == "minus":
					operator = "minus"
				else:
					iteration_data = data.copy()
					for x in iteration_data:
						if "line" in x and x["line"] == c and x["indent"] == 1:
							if i > 0:
								if operator == "plus":
									d["amount"] = value + flt(x["amount"])
								elif operator == "minus":
									d["amount"] = value - flt(x["amount"])
								value = d["amount"]
							else:
								value += flt(x["amount"])

		# If amount is negative exclude it
		if "amount" in d and flt(d["amount"]) < 0:
			d["amount"] = 0

	return data

def get_gl_entries(filters):
	gl_entries = frappe.db.sql(
		"""
		select
			gl.posting_date, gl.accounting_item,
			gl.debit, gl.credit,
			ai.line_2035, ai.code_2035
		from `tabGeneral Ledger Entry` gl
		left join `tabAccounting Item` ai on gl.accounting_item = ai.name
		where practitioner=%(practitioner)s
		and gl.accounting_journal in ('Sales', 'Purchases', 'Miscellaneous operations')
		{conditions}
		order by posting_date, accounting_item
		""".format(
			conditions=get_conditions(filters)
		), filters, as_dict=1)

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

def get_columns(filters):
	currency = "EUR"

	columns = [
		{
			"label": _("Line"),
			"fieldname": "line",
			"fieldtype": "Int",
			"width": 70
		},
		{
			"label": _("Label"),
			"fieldname": "label",
			"fieldtype": "Data",
			"width": 400
		},
		{
			"label": _("Cell"),
			"fieldname": "cell",
			"fieldtype": "Data",
			"width": 50
		},
		{
			"label": _("Amount ({0})".format(currency)),
			"fieldname": "amount",
			"fieldtype": "Float",
			"width": 150
		}
	]

	return columns