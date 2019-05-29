# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import maia
import dateparser
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import cstr, cint, now, formatdate, get_datetime
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.desk.reportview import get_match_cond, get_filters_cond
from maia.maia.utils import parity_gravidity_calculation, get_timeline_data

class PatientRecord(Document):
	def get_feed(self):
		return self.patient_name

	def onload(self):
		"""Load address in `__onload`"""
		load_address_and_contact(self, "patient_record")
		self.load_dashboard_info()
		self.set_gravidity_and_parity()

	def autoname(self):
		self.patient_name = " ".join(filter(None, [cstr(self.get(f)).strip() for f in ["patient_first_name", "patient_last_name"]]))
		self.name = self.get_patient_name()
	
	def after_insert(self):
		dashboard = frappe.new_doc("Custom Patient Record Dashboard")
		dashboard.patient_record = self.name
		try:
			dashboard.insert()
		except Exception as e:
			frappe.log_error("Patient Dashboard Creation Error", e)

	def load_dashboard_info(self):
		fiscal_year = maia.get_default_fiscal_year()
		billing_this_year = frappe.db.sql("""
			select sum(amount)
			from `tabRevenue` 
			where patient=%s
			and docstatus = 1
			and transaction_date >= %s
			and transaction_date <= %s""", (self.name, fiscal_year[1], fiscal_year[2]))

		total_unpaid = frappe.db.sql("""
			select sum(amount)
			from `tabRevenue` 
			where patient=%s
			and party=NULL
			and status != 'Paid'
			and docstatus = 1
			and transaction_date >= %s
			and transaction_date <= %s""", (self.name, fiscal_year[1], fiscal_year[2]))

		social_security_parties = tuple([x["name"] for x in frappe.get_all("Party", filters={"is_social_security": 1})])
		total_unpaid_social_security = frappe.db.sql("""
			select sum(amount)
			from `tabRevenue` 
			where patient=%s
			and party in (%s)
			and status != 'Paid'
			and transaction_date >= %s
			and transaction_date <= %s""", (self.name, social_security_parties, fiscal_year[1], fiscal_year[2]))

		info = {}
		info["billing_this_year"] = billing_this_year[0][0] if billing_this_year else 0
		info["currency"] = maia.get_default_currency()
		info["total_unpaid"] = total_unpaid[0][0] if total_unpaid else 0
		info["total_unpaid_social_security"] = total_unpaid_social_security[0][0] if total_unpaid_social_security else 0

		self.set_onload('dashboard_info', info)

	def get_patient_name(self):
		if frappe.db.get_value("Patient Record", self.patient_name):
			count = frappe.db.sql("""select ifnull(MAX(CAST(SUBSTRING_INDEX(name, ' ', -1) AS UNSIGNED)), 0) from `tabPatient Record` where name like %s""",
								  "%{0} - %".format(self.patient_name), as_list=1)[0][0]
			count = cint(count) + 1

			return "{0} - {1}".format(self.patient_name, cstr(count))

		return self.patient_name

	def validate(self):
		self.patient_name = " ".join(filter(None, [cstr(self.get(f)).strip() for f in ["patient_first_name", "patient_last_name"]]))
		self.validate_cervical_smears()
		self.validate_obtetrical_backgrounds()

	def on_update(self):
		self.set_gravidity_and_parity()

		frappe.db.set_value(self.doctype, self.name, "change_in_patient", 0)
		self.reload()

	def on_trash(self):
		if frappe.db.exists("Custom Patient Record Dashboard", dict(patient_record=self.name)):
			patient_dashboard = frappe.db.get_value('Custom Patient Record Dashboard', dict(patient_record=self.name), 'name')
			try:
				frappe.delete_doc('Custom Patient Record Dashboard', patient_dashboard, force=True)
			except Exception as e:
				frappe.log_error(e)

	def before_rename(self, olddn, newdn, merge=False):
		if frappe.db.exists("Custom Patient Record Dashboard", dict(patient_record=olddn)):
			patient_dashboard = frappe.db.get_value('Custom Patient Record Dashboard', dict(patient_record=olddn), 'name')
			try:
				frappe.delete_doc('Custom Patient Record Dashboard', patient_dashboard, force=True)
			except Exception as e:
				frappe.log_error(e)

	def set_gravidity_and_parity(self):
		gravidity, parity = parity_gravidity_calculation(self.name)

		self.gravidity = gravidity
		self.parity = parity

	def validate_cervical_smears(self):
		for cervical_smear in self.cervical_smear_table:
			date = dateparser.parse((cervical_smear.date.strip()))

			if not date:
				msg = _("Maia cannot read the date {0} at row {1} in your cervical smears table. Please use one of the recommended formats.").format(cervical_smear.date, cervical_smear.idx)
				frappe.log_error(msg)
				frappe.throw(msg, title=_("Error"))

	def validate_obtetrical_backgrounds(self):
		for obstetrical_background in self.obstetrical_backgounds:
			date = dateparser.parse((obstetrical_background.date.strip()))

			if not date:
				msg = _("Maia cannot read the date {0} at row {1} in your obstetrical backgrounds table. Please use one of the recommended formats.").format(obstetrical_background.date, obstetrical_background.idx)
				frappe.log_error(msg)
				frappe.throw(msg, title=_("Error"))


@frappe.whitelist()
def update_weight_tracking(doc, weight):
	weight=frappe.get_doc({
		"doctype": "Weight Tracking",
		"patient_record": doc,
		"date": now(),
		"weight": weight
	}).insert(ignore_permissions=True)

	weight.save()

	return 'Success'

@frappe.whitelist()
def invite_user(patient):
	patient_record = frappe.get_doc("Patient Record", patient)

	if not patient_record.email_id:
		frappe.throw(_("Please set Email Address"))

	try:
		user = frappe.get_doc({
			"doctype": "User",
			"first_name": patient_record.patient_first_name,
			"last_name": patient_record.patient_last_name,
			"email": patient_record.email_id,
			"user_type": "Website User",
			"send_welcome_email": 1
		}).insert(ignore_permissions=True)

		user.append("roles", {
			"doctype": "Has Role",
			"role": "Patient"
		})

		user.save()

	except:
		user = frappe.get_doc("User", patient_record.email_id)
		if user:
			try:
				frappe.delete_doc("User", user.name)
			except:
				return
		return

	try:
		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": patient_record.patient_first_name,
			"last_name": patient_record.patient_last_name,
			"email_id": patient_record.email_id,
			"user": user.name
		}).insert(ignore_permissions=True)
		contact.save()

		contact.append('links', dict(link_doctype='Patient Record', link_name=patient_record.name))
		contact.save()

	except:
		pass

	return user.name


def get_users_for_website(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select name, concat_ws(' ', first_name, middle_name, last_name)
		from `tabUser`
		where enabled=1
			and name not in ("Guest", "Administrator")
			and ({key} like %(txt)s
				or full_name like %(txt)s)
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, full_name), locate(%(_txt)s, full_name), 99999),
			idx desc,
			name, full_name
		limit %(start)s, %(page_len)s""".format(**{
		'key': searchfield,
		'fcond': get_filters_cond(doctype, filters, conditions),
		'mcond': get_match_cond(doctype)
	}), {
		'txt': "%%%s%%" % txt,
		'_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})


@frappe.whitelist()
def get_patient_weight_data(patient_record):

	base_weights = frappe.get_all('Weight Tracking', filters={"patient_record": patient_record}, fields=["date", "weight"])
	pr_weights = frappe.get_all("Pregnancy Consultation", filters={"patient_record": patient_record, "docstatus": 1}, fields=["consultation_date", "weight", "pregnancy_folder"])
	gc_weights = frappe.get_all("Gynecological Consultation", filters={"patient_record": patient_record, "docstatus": 1}, fields=["consultation_date", "weight"])
	pc_weights = frappe.get_all("Postnatal Consultation", filters={"patient_record": patient_record, "docstatus": 1}, fields=["consultation_date", "weight"])

	patient_weight = []

	for base_weight in base_weights:
		if base_weight.weight is not None and base_weight.weight!=0:
			patient_weight.append({'date': base_weight.date, 'weight': base_weight.weight})

	for pr_weight in pr_weights:
		if pr_weight.weight is not None and pr_weight.weight!=0 and isinstance(pr_weight.weight, float):
			patient_weight.append({'date': get_datetime(pr_weight.consultation_date), 'weight': pr_weight.weight, 'pregnancy': pr_weight.pregnancy_folder})

	for gc_weight in gc_weights:
		if gc_weight.weight is not None and gc_weight.weight!=0 and isinstance(gc_weight.weight, float):
			patient_weight.append({'date': get_datetime(gc_weight.consultation_date), 'weight': gc_weight.weight})

	for pc_weight in pc_weights:
		if pc_weight.weight is not None and pc_weight.weight!=0 and isinstance(pc_weight.weight, float):
			patient_weight.append({'date': get_datetime(pc_weight.consultation_date), 'weight': pc_weight.weight})

	patient_weight = sorted(patient_weight, key=lambda x: x["date"])

	titles = []
	values = []
	formatted_x = []
	for pw in patient_weight:
		if "pregnancy" in pw:
			formatted_x.append(formatdate(pw["date"]) + "-" + pw["pregnancy"])
			titles.append(formatdate(pw["date"]))
			values.append(pw["weight"])
		else:
			formatted_x.append(formatdate(pw["date"]))
			titles.append(formatdate(pw["date"]))
			values.append(pw["weight"])

	data = {
		'labels': titles,
		'datasets': [{
			'values': values
			}]
		}

	return data, formatted_x

def get_timeline_data(doctype, name):
	result = dict()
	doctype_list = ['Pregnancy Consultation', 'Birth Preparation Consultation', 'Early Postnatal Consultation', \
		'Postnatal Consultation', 'Perineum Rehabilitation Consultation', 'Gynecological Consultation', \
		'Prenatal Interview Consultation', 'Free Consultation']

	for dt in doctype_list:
		result.update(dict(frappe.db.sql("""select unix_timestamp(date(creation)), count(name)
			from `tab%s`
			where
				date(creation) > subdate(curdate(), interval 1 year)
			and patient_record='%s'
			group by date(creation)
			order by creation asc""" % (dt, name))))

	return result