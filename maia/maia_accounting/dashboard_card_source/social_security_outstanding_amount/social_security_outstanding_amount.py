# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe.utils import nowdate, fmt_money, now
from frappe.core.page.dashboard.dashboard import cache_card_source, get_from_date_from_timespan
from maia.maia_accounting.utils import get_outstanding

@frappe.whitelist()
@cache_card_source
def get(card_name, from_date=None, to_date=None):
	currency = maia.get_default_currency()

	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
	else:
		return fmt_money(0, 0, currency)

	social_security_parties = [x["name"] for x in frappe.get_all("Party", filters={"is_social_security": 1})]
	outstanding = get_outstanding(practitioner, social_security_parties)

	return fmt_money(outstanding or 0, 0, currency)