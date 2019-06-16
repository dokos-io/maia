# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.rename_doc import rename_doc
from frappe.utils import cint
import re

def execute():
	try:
		companies = frappe.get_all("Company", fields=["name", "abbr"])

		for company in companies:
			accounts = frappe.get_all("Account", filters={'company': company.name})

			for account in accounts:
				if account.name[0].isdigit():

					raw_number = re.match("(.*?)-", account.name).group()
					acc_number = raw_number.replace("-", "")

					if raw_number[0].isdigit():

						try:
							rename = (account.name).replace(raw_number, "").strip()
							new_name = acc_number + " - " + rename
							print(new_name)
							rename_doc("Account", account.name, new_name)
						except Exception as e:
							print(e)

		frappe.db.commit()

	except Exception as e:
		print(e)
