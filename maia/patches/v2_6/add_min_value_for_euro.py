# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.set_value("Currency", "EUR", "smallest_currency_fraction_value", 0.01)