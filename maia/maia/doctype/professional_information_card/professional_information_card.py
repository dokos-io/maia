# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class ProfessionalInformationCard(Document):
	pass

@frappe.whitelist()
def create_replacement_user(origin):
	origin = frappe.get_doc("Professional Information Card", origin)

	user = create_user(origin)
	practitioner = create_professional_information_card(user)

	origin.substitute_practitioner = practitioner
	origin.save()

	return practitioner

def create_user(origin):
	if not origin.substitute_email:
		frappe.throw(_("Please set an email address for your substitute"))

	if frappe.db.exists("User", origin.substitute_email):
		new_user = frappe.get_doc("User", origin.substitute_email)
	else:
		new_user = frappe.get_doc({
				"doctype": "User",
				"user_type": "System User",
				"first_name": origin.substitute_first_name,
				"last_name": origin.substitute_last_name,
				"email": origin.substitute_email,
				"send_welcome_email": 0
		}).insert(ignore_permissions = True)

	roles = ["Midwife Substitute"]
	for role in roles:
		if not frappe.db.exists("Role", role):
				role_doc = frappe.get_doc({
						"doctype": "Role",
						"role_name": role
				})
				role_doc.insert()
			
		new_user.append("roles", {
				"doctype": "Has Role",
				"role": role
		})

	new_user.save()

	return new_user

def create_professional_information_card(user):
	if frappe.db.exists("Professional Information Card", {"user": user.name}):
		return frappe.db.get_value("Professional Information Card", {"user": user.name}, "name")

	elif frappe.db.exists("Professional Information Card", {"last_name": user.last_name, "first_name": user.first_name}):
		return frappe.db.get_value("Professional Information Card", {"last_name": user.last_name, "first_name": user.first_name}, "name")
	
	else:
		new_practitioner = frappe.get_doc({
				"doctype": "Professional Information Card",
				"full_name": user.first_name + " " + user.last_name,
				"first_name": user.first_name,
				"last_name": user.last_name,
				"user": user.name
		}).insert(ignore_permissions = True)

		return new_practitioner.name

