from frappe import _

def get_data():
	return [
		{
			"label": _("Maia Templates"),
			"items": [
				{
					"type": "doctype",
					"name": "Default Template",
					"label": _("Default Template"),
					"description": _("Maia Theme"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "One Page Wonder",
					"label": _("One Page Wonder"),
					"description": _("Startbootstrap theme: One Page Wonder"),
					"hide_count": True
				}
			]
		}
	]
