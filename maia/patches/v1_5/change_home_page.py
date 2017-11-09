from __future__ import unicode_literals
import frappe


def execute():
    website_settings = frappe.get_doc(
        'Website Settings', 'Website Settings')
    website_settings.home_page = 'home'
    website_settings.save()

    frappe.db.commit()
