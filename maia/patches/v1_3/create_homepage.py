from __future__ import unicode_literals
import frappe

def execute():
	homepage = frappe.get_doc('Homepage', 'Homepage')
	company = frappe.get_all('Company')

	if company[0].name:
		homepage.company = company[0].name
		homepage.tag_line = company[0].name
		homepage.description = "Connectez-vous pour prendre rendez-vous"
		homepage.save()
