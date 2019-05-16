# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def set_default_settings():
	domain_settings = frappe.get_single('Domain Settings')
	domain_settings.flags.ignore_permissions = True
	domain_settings.set_active_domains(['Sage-Femme'])
