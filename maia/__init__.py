# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import now
from maia.maia_accounting.utils import get_fiscal_year


__version__ = '3.0.0'


def get_default_fiscal_year(user=None):
	'''Get default company for user'''
	if not user:
		user = frappe.session.user

	practitioner = frappe.db.get_value("Professional Information Card", dict(user=user), "name")	

	return  get_fiscal_year(date=now(), practitioner=practitioner)

def get_default_currency():
	'''Returns the currency of the default company'''
	return "EUR"

def get_consultation_types():
	return ["Early Postnatal Consultation", "Pregnancy Consultation", "Postnatal Consultation", "Gynecological Consultation", "Birth Preparation Consultation", \
		"Prenatal Interview Consultation", "Free Consultation", "Perineum Rehabilitation Consultation"]