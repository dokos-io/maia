from frappe import _

def get_data():
	return [
		{
			"label": _("Maia Templates"),
			"items": [
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
