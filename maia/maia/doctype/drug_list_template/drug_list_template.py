# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DrugListTemplate(Document):
	pass

@frappe.whitelist()
def get_drug_list_template(drug_list_template):
	template = frappe.get_doc('Drug List Template', {'name': drug_list_template})
	return template.drug_list_model
