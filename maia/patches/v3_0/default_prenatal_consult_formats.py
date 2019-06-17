from __future__ import unicode_literals
import frappe
from frappe.printing.doctype.print_format.print_format import make_default

def execute():
	frappe.reload_doc('maia', 'print_format', 'prenatal_interview_consultation')
	make_default("Prenatal Interview Consultation")
