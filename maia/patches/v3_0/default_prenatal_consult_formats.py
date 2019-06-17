from __future__ import unicode_literals
import frappe
from frappe.printing.doctype.print_format.print_format import make_default

def execute():
	make_default("Prenatal Interview Consultation")
