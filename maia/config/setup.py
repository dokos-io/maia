# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		{
			"label": _("Core"),
			"items": [
					{
						"type": "doctype",
						"name": "Maia Settings",
						"label": _("Maia Settings"),
						"description": _("Maia Settings")
					}
			]
		}

	]