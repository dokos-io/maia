# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProfessionalInformationCard(Document):
	pass


@frappe.whitelist()
def replacement_user(contact):
        contact = frappe.get_doc("Professional Information Card", contact)

        if not contact.substitute_email:
                frappe.throw(_("Please set Email Address"))

        
        if contact.has_permission("write"):
                user = frappe.get_doc({
                        "doctype": "User",
                        "user_type": "System User",
                        "first_name": contact.substitute_first_name,
                        "last_name": contact.substitute_last_name,
                        "email": contact.substitute_email,
                        "send_welcome_email": 1
                }).insert(ignore_permissions = True)

                roles = ["Accounts User", "Customer", "Item Manager", "Stock User", "Projects User", "Purchase Manager", "Purchase Master Manager", "Purchase User", "Sales Master Manager", "Sales User", "Supplier", "Midwife", "HR User", "Stock Manager"]
                for role in roles:
                        if not frappe.db.exists("Role", role):
                                role_doc = frappe.get_doc({
                                        "doctype": "Role",
                                        "role_name": role
                                })
                                role_doc.save()
                        
                        user.append("roles", {
                                "doctype": "Has Role",
                                "role": role
                        })

                        
                        
                user.save()

                return user.name
