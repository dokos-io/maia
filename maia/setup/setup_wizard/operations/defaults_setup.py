# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def set_default_settings():
	domain_settings = frappe.get_single('Domain Settings')
	domain_settings.flags.ignore_permissions = True
	domain_settings.set_active_domains(['Sage-Femme'])

	frappe.db.set_value('System Settings', None, 'country', 'France')
	frappe.db.set_value('System Settings', None, 'language', 'fr')
	frappe.db.set_value('System Settings', None, 'time_zone', 'heure:France-Europe/Paris')
