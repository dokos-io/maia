# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class ProfessionalInformationCard(Document):
	def before_insert(self):
		if not self.full_name:
			self.full_name = self.first_name + " " + self.last_name

	def validate(self):
		if not self.full_name:
			self.full_name = self.first_name + " " + self.last_name

	def create_user(self):
		user = self.add_user()
		
		if user:
			self.user = user.name
			self.save()

	def add_user(self):
		if not self.email:
			frappe.throw(_("Please add a work email"))

		if frappe.db.exists("User", self.email):
			new_user = frappe.get_doc("User", self.email)
		else:
			try:
				new_user = frappe.get_doc({
						"doctype": "User",
						"user_type": "System User",
						"first_name": self.first_name,
						"last_name": self.last_name,
						"email": self.email,
						"send_welcome_email": 1
				}).insert(ignore_permissions = True)

				roles = ["Midwife Substitute"] if self.is_substitute else ["Midwife", "Midwife Substitute"]
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
			except Exception:
				frappe.log_error(frappe.get_traceback())

		self.user = new_user.name
		self.reload()

		return new_user
