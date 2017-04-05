# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt 

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


@frappe.whitelist()
def print_prescription(doctype, doc, as_print, print_format):
            if cint(as_print):
                        return frappe.get_print(doctype, doc, print_format = print_format)
            else:
                        frappe.throw(_("Print Error: Please contact the technical support."))
    
