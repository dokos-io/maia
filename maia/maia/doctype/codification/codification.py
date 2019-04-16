# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Codification(Document):
	pass

@frappe.whitelist()
def disable_enable_codification(status, name):
	frappe.db.set_value("Codification", name, "disabled", status)
