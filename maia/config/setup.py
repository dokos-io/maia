from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Data"),
			"icon": "fa fa-group",
			"items": [
				{
					"type": "doctype",
					"name": "User",
					"description": _("System and Website Users")
				},
				{
					"type": "doctype",
					"name": "Deleted Document",
					"label": _("Deleted Documents"),
					"description": _("Restore or permanently delete a document.")
				}
			]

		},
		{
			"label": _("Settings"),
			"icon": "fa fa-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "System Settings",
					"label": _("System Settings"),
					"description": _("Language, Date and Time settings"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Letter Head",
					"description": _("Letter Heads for print templates.")
				},
				{
					"type": "doctype",
					"name": "Terms and Conditions",
					"description": _("Standard contract terms for Sales or Purchase.")
				}
			]
		},
		{
			"label": _("Email"),
			"icon": "fa fa-envelope",
			"items": [
				{
					"type": "doctype",
					"name": "Email Account",
					"description": _("Add / Manage Email Accounts.")
				},
				{
					"type": "doctype",
					"name": "Email Domain",
					"description": _("Add / Manage Email Domains.")
				},
				{
					"type": "doctype",
					"name": "Standard Reply",
					"description": _("Standard replies to common queries.")
				},
				{
					"type": "doctype",
					"name": "Auto Email Report",
					"description": _("Setup Reports to be emailed at regular intervals"),
				},
				{
					"type": "doctype",
					"name": "Email Digest",
					"description": _("Create and manage daily, weekly and monthly email digests.")
				}
			]
		},
		{
			"label": _("Printing"),
			"icon": "fa fa-print",
			"items": [
				{
					"type": "page",
					"label": _("Print Format Builder"),
					"name": "print-format-builder",
					"description": _("Drag and Drop tool to build and customize Print Formats.")
				},
				{
					"type": "doctype",
					"name": "Print Format",
					"description": _("Customized HTML Templates for printing transactions.")
				}
			]
		},
		{
			"label": _("Customize"),
			"icon": "fa fa-glass",
			"items": [
				{
					"type": "doctype",
					"name": "Customize Form",
					"description": _("Change field properties (hide, readonly, permission etc.)"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Custom Field",
					"description": _("Add fields to forms.")
				},
				{
					"type": "doctype",
					"label": _("Custom Translations"),
					"name": "Translation",
					"description": _("Add your own translations")
				},
				{
					"type": "doctype",
					"name": "DocType",
					"description": _("Add custom forms.")
				},
				{
					"type": "doctype",
					"label": _("Custom Tags"),
					"name": "Tag Category",
					"description": _("Add your own Tag Categories")
				}
			]
		},
		{
			"label": _("Help"),
			"items": [
				{
					"type": "help",
					"label": _("Setting up Email"),
					"youtube_id": "YFYe0DrB95o"
				},
				{
					"type": "help",
					"label": _("Printing and Branding"),
					"youtube_id": "cKZHcx1znMc"
				}
			]
		}
	]
