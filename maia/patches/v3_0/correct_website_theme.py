# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.get_doc("Default Template", None).build_new_theme()
	frappe.get_doc("One Page Wonder", None).build_new_theme()