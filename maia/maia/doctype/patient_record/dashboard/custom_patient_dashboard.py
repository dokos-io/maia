# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, global_date_format, nowdate
from maia.maia.utils import parity_gravidity_calculation, get_gestational_age
import dateparser
import itertools
import json
from operator import itemgetter

DOMAINS = ["General Info", "Lab Exam", "Pregnancy", "Delivery", "Newborn", "Perineum Rehabilitation", "Gynecology"]

def get_patient_dashboard(patient_record):
	if frappe.db.exists("Custom Patient Record Dashboard", dict(patient_record=patient_record)):
		return frappe.get_doc("Custom Patient Record Dashboard", dict(patient_record=patient_record))

	else:
		dashboard = frappe.new_doc("Custom Patient Record Dashboard")
		dashboard.patient_record = patient_record
		try:
			dashboard.insert()
		except Exception:
			doc = frappe.get_doc("Custom Patient Record Dashboard", patient_record)
			frappe.rename_doc(doc.doctype, patient_record, doc.patient_record, force=True, merge=True if frappe.db.exists(doc.doctype, doc.patient_record) else False)
			return doc

		return dashboard

@frappe.whitelist()
def get_data(patient_record):
	try:
		dashboard = get_patient_dashboard(patient_record)
		patient = frappe.get_doc("Patient Record", patient_record)
		data={
			"generaldata": {
				"icon": "/assets/maia/images/general.svg"
			},
			"gynecologydata": {
				"icon": "/assets/maia/images/gynecology.svg"
			},
			"pregnancydata": {
				"icon": "/assets/maia/images/pregnancy.svg"
			},
			"deliverydata":{
				"icon": "/assets/maia/images/delivery.svg"
			},
			"newborndata": {
				"icon": "/assets/maia/images/newborn.svg"
			},
			"labexamsdata": {
				"icon": "/assets/maia/images/lab_exam_results.svg"
			},
			"perehabilitationdata": {
				"icon": "/assets/maia/images/perineum_rehabilitation.svg"
			}
		}

		latest_pregnancy = get_last_pregnancy(patient_record)
		patient_latest_pregnancy = frappe.get_doc("Pregnancy", latest_pregnancy[0].name) if latest_pregnancy else None

		gynecology_folders = frappe.get_all("Gynecology", dict(patient_record=patient_record))

		#General section
		#Gravidity and parity
		gravidity, parity = parity_gravidity_calculation(patient_record)
		data["generaldata"]["gravidity"] = {
			"label": _("Gestity"),
			"value": gravidity,
			"color": "#ff4081",
			"enabled": 1 if dashboard.gravidity_parity else 0
		}
		data["generaldata"]["parity"] = {
			"label": _("Parity"),
			"color": "#ff4081",
			"value": parity,
			"enabled": 1 if dashboard.gravidity_parity else 0
		}

		#Allergies
		data["generaldata"]["allergies"] = {
			"label": _("Allergies"),
			"value": patient.allergies,
			"enabled": 1 if dashboard.allergies and patient.allergies else 0,
			"value_fields": ["patient_allergies"]
		}

		#Medical Background
		data["generaldata"]["medical_background"] = {
			"label": _("Medical Background"),
			"value": patient.long_term_disease,
			"enabled": 1 if dashboard.medical_background and patient.long_term_disease else 0
		}

		#Addictions
		data["generaldata"]["addictions"] = {
			"label": _("Addictions"),
			"value": patient.patient_addictions,
			"enabled": 1 if dashboard.addictions and patient.patient_addictions else 0,
			"value_fields": ["patient_addictions"]
		}

		#Blood type
		blood_group = frappe.db.get_value("Patient Record", patient_record, "blood_group")
		negative_list = ["A-", "B-", "AB-", "O-"]
		data["generaldata"]["blood_group"] = {
			"label": _("Blood Group"),
			"value": blood_group, 
			"color": "#ff5858" if blood_group in negative_list else "#36414c",
			"enabled": 1 if dashboard.blood_group and blood_group != "" else 0
		}

		#Gynecology Section
		#Cervical Smear
		data["gynecologydata"]["cervical_smear"] = {
			"label": _("Last Cervical Smear"), 
			"value": get_last_cervical_smear(patient_record),
			"enabled" : 1 if dashboard.cervical_smear else 0,
			"value_fields": ["date", "result"]
		}

		#Current Contraception
		data["gynecologydata"]["contraception"] = {
			"label": _("Current Contraception"), 
			"value": patient.contraception,
			"enabled": 1 if dashboard.contraception and patient.contraception else 0
		}

		#Screening Tests
		data["gynecologydata"]["screening_tests"] = {
			"label": _("Last Screening Test"),
			"value": get_last_screening_test(patient_record),
			"enabled": 1 if dashboard.screening_tests else 0,
			"value_fields": ["date"]
		}

		#Lipid Profile
		data["gynecologydata"]["lipid_profile"] = {
			"label": _("Last Lipid Profile"),
			"value": get_last_lipid_profile(patient_record),
			"enabled": 1 if dashboard.lipid_profile else 0,
			"value_fields": ["date"]
		}

		#Mammography
		data["gynecologydata"]["mammography"] = {
			"label": _("Last Mammography"), 
			"value": get_last_mammography(patient_record),
			"enabled": 1 if dashboard.mammography else 0,
			"value_fields": ["date"]
		}

		#Pregnancy Section
		#Beginning of Pregnancy
		data["pregnancydata"]["beginning_of_pregnancy"] = {
			"label": _("Beginning of Pregnancy"), 
			"value": global_date_format(patient_latest_pregnancy.beginning_of_pregnancy) \
				if patient_latest_pregnancy and patient_latest_pregnancy.beginning_of_pregnancy is not None else None,
			"enabled": 1 if dashboard.beginning_of_pregnancy else 0,
			"alter_text": _("Please set the beginning of pregnancy date in your latest pregnancy folder")
		}

		#Expected Term
		data["pregnancydata"]["expected_term"] = {
			"label": _("Expected Term"), 
			"value": global_date_format(patient_latest_pregnancy.expected_term) \
				if patient_latest_pregnancy and patient_latest_pregnancy.expected_term is not None else None,
			"enabled": 1 if dashboard.expected_term else 0,
			"alter_text": _("Please set the expected term date in your latest pregnancy folder")
		}

		#Preferred Location for Delivery
		data["pregnancydata"]["preferred_location_for_delivery"] = {
			"label": _("Preferred Location for Delivery"),
			"value": patient_latest_pregnancy.preferred_location_for_delivery if latest_pregnancy else None,
			"enabled": 1 if dashboard.preferred_location_for_delivery else 0
		}

		#Pregnancy Complications
		data["pregnancydata"]["pregnancy_complications"] = {
			"label": _("Pregnancy Complications"),
			"value": patient_latest_pregnancy.pregnancy_complications if latest_pregnancy else None,
			"enabled": 1 if dashboard.pregnancy_complications else 0
		}

		#Gestational Age
		data["pregnancydata"]["gestational_age"] = {
			"label": _("Gestational Age"),
			"value": format_gestational_age(get_gestational_age(patient_latest_pregnancy, nowdate())) if (latest_pregnancy and not patient_latest_pregnancy.date_time) else None,
			"enabled": 1 if dashboard.gestational_age else 0
		}

		#Lab Exam Section
		#Exam Results
		data["labexamsdata"]["exam_results"] = {
			"value_label": "label",
			"value_fields": ["value"],
			"value": []
		}

		enabled = 0
		for folder in gynecology_folders:
			doc = frappe.get_doc("Gynecology", folder)
			for result in doc.labs_results:
				if result.show_on_dashboard:
					enabled = 1 if dashboard.exam_results else enabled
					r = {
						"date": global_date_format(result.date),
						"label": _(result.exam_type),
						"value": result.exam_result,
						"enabled": 1 if dashboard.exam_results else 0
					}
					data["labexamsdata"]["exam_results"]["value"].append(r)

		if latest_pregnancy:
			for results in patient_latest_pregnancy.labs_results:
				if results.show_on_dashboard:
					enabled = 1 if dashboard.exam_results else enabled
					r = {
						"date": global_date_format(results.date),
						"label": _(results.exam_type),
						"value": results.exam_result,
						"enabled": 1 if dashboard.exam_results else 0
					}
					data["labexamsdata"]["exam_results"]["value"].append(r)
		
		data["labexamsdata"]["exam_results"]["enabled"] = enabled
					

		#Delivery Section
		#Delivery Date
		delivery_date = patient_latest_pregnancy.date_time if latest_pregnancy else None

		data["deliverydata"]["delivery_date"] = {
			"label": _("Delivery Date"),
			"value": global_date_format(getdate(delivery_date)) if delivery_date is not None else None,
			"enabled": 1 if dashboard.delivery_date else 0,
			"alter_text": _("Please set a delivery date in your latest pregnancy folder")
		}

		#Delivery Type
		delivery_way = patient_latest_pregnancy.delivery_way if latest_pregnancy else None
		data["deliverydata"]["delivery_way"] = {
			"label": _("Delivery Way"),
			"value": delivery_way,
			"enabled": 1 if dashboard.delivery_way else 0
		}

		#Delivery Complications
		delivery_complications = patient_latest_pregnancy.anesthesia_complications \
			if latest_pregnancy and patient_latest_pregnancy.anesthesia_complications else None
		data["deliverydata"]["delivery_complications"] = {
			"label": _("Delivery Complications"),
			"value": delivery_complications,
			"enabled": 1 if dashboard.delivery_complications else 0
		}

		#Scar
		scar = patient_latest_pregnancy.scar if latest_pregnancy else None
		data["deliverydata"]["scar"] = {
			"label": _("Scar"),
			"value": scar,
			"enabled": 1 if dashboard.scar else 0
		}

		#Child Section
		data["newborndata"]["firstchild"] = {}
		data["newborndata"]["secondchild"] = {}
		data["newborndata"]["thirdchild"] = {}

		#Child Name
		first_child_name = patient_latest_pregnancy.full_name if latest_pregnancy else None
		second_child_name = patient_latest_pregnancy.full_name_2 \
			if latest_pregnancy and (patient_latest_pregnancy.twins or patient_latest_pregnancy.triplets) \
			else None
		third_child_name = patient_latest_pregnancy.full_name_3 if latest_pregnancy and \
			patient_latest_pregnancy.triplets else None

		data["newborndata"]["firstchild"]["child_name"] = {
			"label": _("Child name"),
			"value": first_child_name,
			"enabled": 1 if dashboard.child_name else 0
		}

		data["newborndata"]["secondchild"]["child_name"] = {
			"label": _("Child name"),
			"value": second_child_name,
			"enabled": 1 if dashboard.child_name else 0
		}

		data["newborndata"]["thirdchild"]["child_name"] = {
			"label": _("Child name"),
			"value": third_child_name,
			"enabled": 1 if dashboard.child_name else 0
		}

		#Child Weight
		first_child_weight = patient_latest_pregnancy.birth_weight if latest_pregnancy else None
		second_child_weight = patient_latest_pregnancy.birth_weight_2 if latest_pregnancy and \
			(patient_latest_pregnancy.twins or patient_latest_pregnancy.triplets) else None
		third_child_weight = patient_latest_pregnancy.birth_weight_3 if latest_pregnancy and \
			patient_latest_pregnancy.triplets else None

		data["newborndata"]["firstchild"]["birth_weight"] = {
			"label": _("Birth Weight"),
			"value": first_child_weight,
			"enabled": 1 if dashboard.birth_weight else 0
		}

		data["newborndata"]["secondchild"]["birth_weight"] = {
			"label": _("Birth Weight"),
			"value": second_child_weight,
			"enabled": 1 if dashboard.birth_weight else 0
		}

		data["newborndata"]["thirdchild"]["birth_weight"] = {
			"label": _("Birth Weight"),
			"value": third_child_weight,
			"enabled": 1 if dashboard.birth_weight else 0
		}

		#Feeding Type
		first_child_feeding = patient_latest_pregnancy.feeding_type if latest_pregnancy else None
		second_child_feeding = patient_latest_pregnancy.feeding_type_2 if latest_pregnancy and \
			(patient_latest_pregnancy.twins or patient_latest_pregnancy.triplets) else None
		third_child_feeding = patient_latest_pregnancy.feeding_type_3 if latest_pregnancy and \
			patient_latest_pregnancy.triplets else None

		data["newborndata"]["firstchild"]["feeding_type"] = {
			"label": _("Feeding Type"),
			"value": first_child_feeding,
			"enabled": 1 if dashboard.feeding_type else 0
		}

		data["newborndata"]["secondchild"]["feeding_type"] = {
			"label": _("Feeding Type"),
			"value": second_child_feeding,
			"enabled": 1 if dashboard.feeding_type else 0
		}

		data["newborndata"]["thirdchild"]["feeding_type"] = {
			"label": _("Feeding Type"),
			"value": third_child_feeding,
			"enabled": 1 if dashboard.feeding_type else 0
		}

		#Perineum Rehabilitation Section
		#Get latest folder
		folder = get_last_perineum_rehabilitation(patient_record)
		pr_folder = frappe.get_doc("Perineum Rehabilitation", folder[0].name) if folder else None

		#Urgency of Urination
		data["perehabilitationdata"]["urgency_of_urination"] = {
			"label": _("Urgency of urination"),
			"value": _(pr_folder.urgency_of_urination) if pr_folder else None,
			"enabled": 1 if dashboard.urgency_of_urination else 0
		}

		#Overactive Bladder
		data["perehabilitationdata"]["overactive_bladder"] = {
			"label": _("Overactive Bladder"),
			"value": _(pr_folder.overactive_bladder) if pr_folder else None,
			"enabled": 1 if dashboard.overactive_bladder else 0
		}

		#Testing
		data["perehabilitationdata"]["testing"] = {
			"label": _("Testing"),
			"value": pr_folder.testing if pr_folder else None,
			"enabled": 1 if dashboard.testing else 0
		}
	except Exception:
		print(frappe.get_traceback())

	return enable_dashboard_modules(data)

def enable_dashboard_modules(data):
	for d in data:
		enabled = 0
		for k, v in data[d].items():
			if isinstance(v, dict):
				try:
					for l, w in data[d][k].items():
						if isinstance(w, dict):
							enabled = 1 if data[d][k][l]["enabled"] == 1 else enabled
						else:
							enabled = 1 if data[d][k]["enabled"] == 1 else enabled
				except Exception:
					frappe.log_error(frappe.get_traceback(), "Maia dashboard error")
			elif isinstance(v, str):
				continue
			else:
				for m in data[d][k]:
					enabled = 1 if m.enabled == 1 else enabled
		
		data[d]["enabled"] = enabled
	
	return data

def get_last_pregnancy(patient_record):
	dates = frappe.get_all("Pregnancy", filters={"patient_record": patient_record}, fields=["name", "beginning_of_pregnancy", "expected_term", "last_menstrual_period", "date_time"])

	if all(date.beginning_of_pregnancy is None for date in dates) == False:
		latest_beginning_of_pregnancy = max(date.beginning_of_pregnancy for date in dates if date.beginning_of_pregnancy is not None)
	else:
		latest_beginning_of_pregnancy = "1900-01-01"

	if all(date.expected_term is None for date in dates) == False:
		latest_expected_term = max(date.expected_term for date in dates if date.expected_term is not None)
	else:
		latest_expected_term = "1900-01-01"

	if all(date.last_menstrual_period is None for date in dates) == False:
		latest_last_menstrual_period = max(date.last_menstrual_period for date in dates if date.last_menstrual_period is not None)
	else:
		latest_last_menstrual_period = "1900-01-01"

	if all(date.date_time is None for date in dates) == False:
		date_time = max(date.date_time for date in dates if date.date_time is not None)
	else:
		date_time = "1900-01-01"

	d = {"beginning_of_pregnancy":getdate(latest_beginning_of_pregnancy), "expected_term":getdate(latest_expected_term), "last_menstrual_period":getdate(latest_last_menstrual_period), "date_time": getdate(date_time)}

	latest_date=max(d.keys(), key = (lambda x: d[x]))

	if latest_date == "date_time":
		last_pregnancy = frappe.get_all("Pregnancy", filters={"patient_record": patient_record, "date_time": date_time})
	else:
		last_pregnancy = frappe.get_all("Pregnancy", filters={"patient_record": patient_record, latest_date: d[latest_date]})

	return last_pregnancy

def get_last_perineum_rehabilitation(patient_record):
	folders = frappe.get_all("Perineum Rehabilitation", filters={"patient_record": patient_record}, fields=["name", "modified"])

	if not folders:
		return []

	else:
		latest = max(folder.modified for folder in folders)

		latest_folder = frappe.get_all("Perineum Rehabilitation", filters={"patient_record": patient_record, "modified": latest})

		return latest_folder

def get_last_cervical_smear(patient_record):
	doc = frappe.get_doc("Patient Record", patient_record)
	cervical_smears = doc.cervical_smear_table

	if cervical_smears:
		for cervical_smear in cervical_smears:
			cervical_smear.update({"date_time": dateparser.parse((cervical_smear.date.strip()) \
				if (cervical_smear.date is not None) else nowdate())})

		latest = max(cervical_smear.date_time for cervical_smear in cervical_smears)
		latest_cs = [cs for cs in cervical_smears if cs.date_time == latest]
		return latest_cs

def get_last_screening_test(patient_record):
	gynecological_folders = frappe.get_all("Gynecology", dict(patient_record=patient_record))

	if gynecological_folders:
		screening_tests = []
		for gynecological_folder in gynecological_folders:
			doc = frappe.get_doc("Gynecology", gynecological_folder.name)
			if doc.screening_tests:
				for test in doc.screening_tests :
					screening_tests.append(test)

		if screening_tests:
			for screening_test in screening_tests:
				screening_test.update({"date_time": dateparser.parse((screening_test.date.strip()) if (screening_test.date is not None) else nowdate())})

			latest = max(screening_test.date_time for screening_test in screening_tests)
			latest_st = [st for st in screening_tests if st.date_time == latest]
			return latest_st
		else:
			return []

def get_last_lipid_profile(patient_record):
	gynecological_folders = frappe.get_all("Gynecology", dict(patient_record=patient_record))


	if gynecological_folders:
		lipid_profiles = []
		for gynecological_folder in gynecological_folders:
			doc = frappe.get_doc("Gynecology", gynecological_folder.name)
			if doc.lipid_profile:
				for test in doc.lipid_profile :
					lipid_profiles.append(test)

		if lipid_profiles:
			for lipid_profile in lipid_profiles:
				lipid_profile.update({"date_time": dateparser.parse((lipid_profile.date.strip()) if (lipid_profile.date is not None) else nowdate())})

			latest = max(lipid_profile.date_time for lipid_profile in lipid_profiles)
			latest_lp = [lp for lp in lipid_profiles if lp.date_time == latest]
			return latest_lp
		else:
			return []

def get_last_mammography(patient_record):
	gynecological_folders = frappe.get_all("Gynecology", dict(patient_record=patient_record))

	if gynecological_folders:
		mammographies = []
		for gynecological_folder in gynecological_folders:
			doc = frappe.get_doc("Gynecology", gynecological_folder.name)
			if doc.mammographies_table:
				for test in doc.mammographies_table :
					mammographies.append(test)

		if mammographies:
			for mammography in mammographies:
				mammography.update({"date_time": dateparser.parse((mammography.date.strip()) if (mammography.date is not None) else nowdate())})

			latest = max(mammography.date_time for mammography in mammographies)
			latest_m = [m for m in mammographies if m.date_time == latest]
			return latest_m
		else:
			return []


@frappe.whitelist()
def get_options(patient_record):
	dashboard = get_patient_dashboard(patient_record)

	result = []
	for field in dashboard.meta.fields:
		if field.options in DOMAINS:
			label = field.label
			option = field.options
			attr = field.fieldname
			prev_value = dashboard.get(field.fieldname)

			result.append({"name": attr, "label": _(label), "value": prev_value, "option": option})

	sorted_result = sorted(result, key=itemgetter("option"))

	final_result = []
	for key, group in itertools.groupby(sorted_result, key=lambda x:x["option"]):
		final_result.append({_(key): list(group)})

	return final_result

@frappe.whitelist()
def update_dashboard(patient_record, options):
	options = json.loads(options)

	if options:
		for option in options:
			for key, value in option.items():
				frappe.db.set_value("Custom Patient Record Dashboard", dict(patient_record=patient_record), key, value)
				frappe.db.commit()

	return "Success"

def format_gestational_age(values):
	return _("{0} Weeks Amenorrhea + {1} Days").format(values[0], values[1])