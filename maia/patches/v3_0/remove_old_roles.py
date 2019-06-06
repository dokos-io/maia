# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.core.doctype.user_permission.user_permission import clear_user_permissions

def execute():
	frappe.reload_doc('maia_appointment', 'doctype', 'maia_appointment')
	frappe.reload_doc('maia_appointment', 'doctype', 'maia_appointment_type')
	frappe.reload_doc('maia', 'doctype', 'professional_information_card')
	frappe.reload_doc('email', 'doctype', 'auto_email_report')
	frappe.reload_doc('geo', 'doctype', 'currency')
	frappe.reload_doc('contacts', 'doctype', 'address', force=True, reset_permissions=True)
	frappe.reload_doc('contacts', 'report', 'addresses_and_contacts', force=True, reset_permissions=True)
	frappe.reload_doc('desk', 'doctype', 'auto_repeat')

	users = frappe.get_all("User")
	kept_roles = ["Midwife", "System Manager", "Midwife Substitute", "Patient", "Appointment User", "Administrator", "Guest", \
		"All", "Blogger", "Website Manager", "Knowledge Base Contributor", "Knowledge Base Editor", "Newsletter Manager", "Report Manager"]
	roles = frappe.db.sql_list("""select name from `tabRole` where name not in {0}""".format(tuple(kept_roles)))

	for user in users:
		user_roles = frappe.get_roles(user.name)
		frappe.db.sql("""DELETE FROM `tabHas Role` WHERE parent=%s""", user.name)

		clear_user_permissions(user.name, "Company")
		clear_user_permissions(user.name, "Employee")
		frappe.db.commit()
		frappe.clear_cache()

		user_doc = frappe.get_doc("User", user.name)
		if user_doc.user_type == "Website User":
			user_doc.add_roles("Patient")
			frappe.db.set_value("User", user_doc.name, "user_type", "Website User")
		else:
			if "Appointment User" in user_roles:
				user_doc.add_roles("Appointment User")
				user_doc.add_roles("Patient")
				user_doc.add_roles("Website Manager")
				user_doc.add_roles("Blogger")
			else:
				user_doc.add_roles("Midwife")
				user_doc.add_roles("Patient")
				user_doc.add_roles("Website Manager")
				user_doc.add_roles("Report Manager")
				user_doc.add_roles("Blogger")

			user_doc.append('block_modules', {
				'module': 'Integrations'
			})
			user_doc.append('block_modules', {
				'module': 'Customization'
			})
			user_doc.save()

	frappe.db.set_value("User", "Guest", "user_type", "Website User")

	for role in roles:
		try:
			frappe.db.sql("""DELETE FROM `tabHas Role` WHERE role=%s""", role)
			frappe.db.commit()
			frappe.delete_doc("Role", role, force=True)
		except Exception as e:
			print("Role: " + role)
			print(e)

	# Add the default sms values in professional informations cards
	cards = frappe.get_all("Professional Information Card")

	for card in cards:
		frappe.db.set_value("Professional Information Card", card.name, "sms_content", \
			"Rappel: Vous avez rendez-vous avec {midwife} le {date} à {time}. En cas d'impossibilité, veuillez contacter votre sage-femme. Merci")