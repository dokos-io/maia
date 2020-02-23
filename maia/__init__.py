# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import now
from maia.maia_accounting.utils import get_fiscal_year


__version__ = '3.1.5'


def get_default_fiscal_year(user=None):
	if not user:
		user = frappe.session.user

	practitioner = frappe.db.get_value("Professional Information Card", dict(user=user), "name")	

	return  get_fiscal_year(date=now(), practitioner=practitioner)

def get_default_currency():
	return frappe.defaults.get_defaults().get("currency")

def get_consultation_types():
	return ["Early Postnatal Consultation", "Pregnancy Consultation", "Postnatal Consultation", "Gynecological Consultation", "Birth Preparation Consultation", \
		"Prenatal Interview Consultation", "Free Consultation", "Perineum Rehabilitation Consultation"]

def get_practitioner(user=None):
	if not user:
		user = frappe.session.user

	return frappe.db.get_value("Professional Information Card", dict(user=user), "name")
