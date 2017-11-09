from __future__ import unicode_literals
import frappe
from frappe.printing.doctype.print_format.print_format import make_default


def execute():
    print_formats = ["Postnatal Consultation",
                     "Birth Preparation Consultation", "Perineum Rehabilitation Consultation"]

    for print_format in print_formats:
        make_default(print_format)
