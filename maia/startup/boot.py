# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt"


from __future__ import unicode_literals
import frappe
from frappe.utils import cint, now
from maia.maia_accounting.utils import get_fiscal_year

def boot_session(bootinfo):
	"""boot session - send website info if guest"""

	bootinfo.website_settings = frappe.get_doc('Website Settings')

	if frappe.session['user']!='Guest':

		load_country_and_currency(bootinfo)

		bootinfo.practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
		bootinfo.fiscal_year = get_fiscal_year(date=now(), practitioner=bootinfo.practitioner)

def load_country_and_currency(bootinfo):
	country = frappe.db.get_default("country")
	if country and frappe.db.exists("Country", country):
		bootinfo.docs += [frappe.get_doc("Country", country)]

	bootinfo.docs += frappe.db.sql("""select name, fraction, fraction_units,
		number_format, smallest_currency_fraction_value, symbol from tabCurrency
		where enabled=1""", as_dict=1, update={"doctype":":Currency"})
