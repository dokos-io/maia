# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, global_date_format
from frappe import _


def execute():
    language = frappe.get_single("System Settings").language
    frappe.local.lang = language
    patient_records = frappe.get_all('Patient Record')
    pregnancies = frappe.get_all('Pregnancy')

    for patient_record in patient_records:

        pr = frappe.get_doc("Patient Record", patient_record)

        message = ""

        if pr.parity is not None:
            message = '<div>Parité au ' + global_date_format(nowdate()) + ": "
            message += str(pr.parity)

            message += '</div><br>'

        if pr.gravidity is not None:
            message += '<div>Gestité au ' + global_date_format(nowdate()) + ": "
            message += str(pr.gravidity) + '</div>'

        pr.add_comment('Comment', message)
        frappe.db.commit()

    for pregnancy in pregnancies:

        pr = frappe.get_doc("Pregnancy", pregnancy)

        message = ""

        if pr.parity is not None:
            message = '<div>Parité au ' + global_date_format(nowdate()) + ": "
            message += str(pr.parity)

            message += '</div><br>'

        if pr.gravidity is not None:
            message += '<div>Gestité au ' + global_date_format(nowdate()) + ": "
            message += str(pr.gravidity) + '</div>'

        pr.add_comment('Comment', message)
        frappe.db.commit()

    delivery_ways = frappe.get_all("Delivery Way")

    for delivery_way in delivery_ways:
        if delivery_way.name in [_("Normal"), _("Vacuum"), _("Forceps"), _("Spatulas"), _("Emergency C-Section"), _("Before Labour C-Section")]:
            frappe.db.set_value("Delivery Way", delivery_way, 'used_in_parity', 1)
            frappe.db.commit()


    records = [
    {'doctype': "Delivery Way", 'delivery_way': _("Therapeutic Abortion Sup To 22 WA"), 'used_in_parity': 1},
    {'doctype': "Delivery Way", 'delivery_way': _("Therapeutic Abortion Inf To 22 WA"), 'used_in_parity': 0},
    {'doctype': "Delivery Way", 'delivery_way': _("Surgical Abortion"), 'used_in_parity': 0},
    {'doctype': "Delivery Way", 'delivery_way': _("Drug Induced Abortion"), 'used_in_parity': 0},
    {'doctype': "Delivery Way", 'delivery_way': _("Miscarriage"), 'used_in_parity': 0},
    {'doctype': "Delivery Way", 'delivery_way': _("Ectopic Pregnancy"), 'used_in_parity': 0}
    ]

    from frappe.modules import scrub
    for r in records:
        print(r)
        doc = frappe.new_doc(r.get("doctype"))
        doc.update(r)

        try:
            doc.insert(ignore_permissions=True)
        except frappe.DuplicateEntryError as e:
            print(e)
            # pass DuplicateEntryError and continue
            if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
                # make sure DuplicateEntryError is for the exact same doc and not a related doc
                pass
            else:
                raise
    frappe.db.commit()
