# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


def execute():
    frappe.db.set_value("Global Defaults", None, "disable_rounded_total", 1)
