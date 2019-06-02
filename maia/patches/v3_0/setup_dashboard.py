# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from from maia.setup.setup_wizard.operations.dashboard_setup import setup_charts, setup_cards, init_dashboard

def execute():
	setup_charts()
	setup_cards()
	init_dashboard()