# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, global_date_format
import json

DASHBOARD_LIST = ["beginning_of_pregnancy", "exam_results", "pregnancy_complications", "delivery_way", "child_name", "delivery_date", "blood_group",
                    "allergies", "medical_background", "addictions", "gravidity_parity", "expected_term", "preferred_location_for_delivery", "delivery_complications",
                    "scar", "birth_weight", "feeding_type", "urgency_of_urination", "overactive_bladder", "testing"]

def get_patient_dashboard(patient_record):
    if frappe.db.exists("Custom Patient Record Dashboard", dict(patient_record=patient_record)):
        return frappe.get_doc("Custom Patient Record Dashboard", dict(patient_record=patient_record))

    else:
        dashboard = frappe.new_doc("Custom Patient Record Dashboard")
        dashboard.patient_record = patient_record
        dashboard.save()

        return dashboard

@frappe.whitelist()
def get_data(patient_record):
    dashboard = get_patient_dashboard(patient_record)
    patient = frappe.get_doc("Patient Record", patient_record)
    data=[]
    generaldata = {}
    pregnancydata = {}
    deliverydata = {}
    newborndata = {}
    labexamsdata = {}
    perehabilitationdata = {}

    latest_pregnancy = get_last_pregnancy(patient_record)
    if latest_pregnancy:
        patient_latest_pregnancy = frappe.get_doc("Pregnancy", latest_pregnancy[0].name)


    #General Section
    #Gravidity
    if dashboard.gravidity_parity:
        generaldata['gravidity'] = patient.gravidity

    #Parity
    if dashboard.gravidity_parity:
        generaldata['parity'] = patient.parity

    #Allergies
    if dashboard.allergies:
        generaldata['allergies'] = patient.allergies

    #Medical Background
    if dashboard.medical_background:
        generaldata['medical_background'] = patient.long_term_disease

    #Addictions
    if dashboard.addictions:
        generaldata['addictions'] = patient.patient_addictions

    #Blood type
    if dashboard.blood_group:
        blood_group = frappe.db.get_value("Patient Record", patient_record, "blood_group")
        negative_list = ["A-", "B-", "AB-", "O-"]
        if blood_group in negative_list:
            color = "red"
        else:
            color = "black"
        generaldata['blood_group'] = {"name": blood_group, "color": color}

    #Pregnancy Section
    #Beginning of Pregnancy
    if dashboard.beginning_of_pregnancy:
        if latest_pregnancy:
            if patient_latest_pregnancy.beginning_of_pregnancy is not None:
                pregnancydata['beginning_of_pregnancy'] = global_date_format(patient_latest_pregnancy.beginning_of_pregnancy)
        else:
            pregnancydata['beginning_of_pregnancy'] = None

    #Expected Term
    if dashboard.expected_term:
        if latest_pregnancy:
            if patient_latest_pregnancy.expected_term is not None:
                pregnancydata['expected_term'] = global_date_format(patient_latest_pregnancy.expected_term)
        else:
            pregnancydata['expected_term'] = None

    #Preferred Location for Delivery
    if dashboard.preferred_location_for_delivery:
        if latest_pregnancy:
            pregnancydata['preferred_location_for_delivery'] = patient_latest_pregnancy.preferred_location_for_delivery

    #Pregnancy Complications
    if dashboard.pregnancy_complications:
        if latest_pregnancy:
            pregnancydata['pregnancy_complications'] = patient_latest_pregnancy.pregnancy_complications

    #Lab Exam Section
    #Exam Results
    if dashboard.exam_results:
        labexamsdata['exam_results'] = []

        if latest_pregnancy:
            for results in patient_latest_pregnancy.labs_results:
                if results.show_on_dashboard:
                    results.date = global_date_format(results.date)
                    labexamsdata['exam_results'].append(results)
        else:
            labexamsdata['exam_results'] = None

    #Delivery Section
    #Delivery Date
    if dashboard.delivery_date:
        if latest_pregnancy:
            delivery_date = patient_latest_pregnancy.date_time

            if delivery_date is not None:
                deliverydata['delivery_date'] = global_date_format(getdate(delivery_date))
            else:
                deliverydata['delivery_date'] = None

    #Delivery Type
    if dashboard.delivery_way:
        if latest_pregnancy:
            delivery_way = patient_latest_pregnancy.delivery_way
            deliverydata['delivery_way'] = delivery_way

    #Delivery Complications
    if dashboard.delivery_complications:
        if latest_pregnancy:
            delivery_complications = patient_latest_pregnancy.anesthesia_complications
            deliverydata['delivery_complications'] = delivery_complications

    #Scar
    if dashboard.scar:
        if latest_pregnancy:
            scar = patient_latest_pregnancy.scar
            deliverydata['scar'] = scar

    #Child Section
    newborndata['firstchild'] = {}
    newborndata['secondchild'] = {}
    newborndata['thirdchild'] = {}
    #Child Name
    if dashboard.child_name:
        if latest_pregnancy:
            if patient_latest_pregnancy.full_name:
                newborndata['firstchild'].update({'child_name': patient_latest_pregnancy.full_name})
            if (patient_latest_pregnancy.twins or patient_latest_pregnancy.triplets) and patient_latest_pregnancy.full_name_2:
                newborndata['secondchild'].update({'child_name': patient_latest_pregnancy.full_name_2})
            if patient_latest_pregnancy.triplets and patient_latest_pregnancy.full_name_3:
                newborndata['thirdchild'].update({'child_name': patient_latest_pregnancy.full_name_3})

    #Child Weight
    if dashboard.birth_weight:
        if latest_pregnancy:
            if patient_latest_pregnancy.birth_weight:
                newborndata['firstchild'].update({'birth_weight': patient_latest_pregnancy.birth_weight})
            if (patient_latest_pregnancy.twins or patient_latest_pregnancy.triplets) and patient_latest_pregnancy.birth_weight_2:
                newborndata['secondchild'].update({'birth_weight': patient_latest_pregnancy.birth_weight_2})
            if patient_latest_pregnancy.triplets and patient_latest_pregnancy.birth_weight_3:
                newborndata['thirdchild'].update({'birth_weight': patient_latest_pregnancy.birth_weight_3})

    #Feeding Type
    if dashboard.feeding_type:
        if latest_pregnancy:
            if patient_latest_pregnancy.feeding_type:
                newborndata['firstchild'].update({'feeding_type': patient_latest_pregnancy.feeding_type})
            if (patient_latest_pregnancy.twins or patient_latest_pregnancy.triplets) and patient_latest_pregnancy.feeding_type_2:
                newborndata['secondchild'].update({'feeding_type': patient_latest_pregnancy.feeding_type_2})
            if patient_latest_pregnancy.triplets and patient_latest_pregnancy.feeding_type_3:
                newborndata['thirdchild'].update({'feeding_type': patient_latest_pregnancy.feeding_type_3})

    #Perineum Rehabilitation Section
    #Get latest folder
    if dashboard.urgency_of_urination or dashboard.overactive_bladder or dashboard.testing:
        folder = get_last_perineum_rehabilitation(patient_record)
        pr_folder = frappe.get_doc("Perineum Rehabilitation", folder[0].name)

        #Urgency of Urination
        if dashboard.urgency_of_urination:
            perehabilitationdata['urgency_of_urination'] = _(pr_folder.urgency_of_urination)

        #Overactive Bladder
        if dashboard.overactive_bladder:
            perehabilitationdata['overactive_bladder'] = _(pr_folder.overactive_bladder)

        #Testing
        if dashboard.testing:
            perehabilitationdata['testing'] = pr_folder.testing


    if generaldata:
        data.append({'general': generaldata})

    if pregnancydata:
        data.append({'pregnancy': pregnancydata})

    if deliverydata:
        data.append({'delivery': deliverydata})

    if newborndata['firstchild'] or newborndata['secondchild'] or newborndata['thirdchild']:
        data.append({'newborn': newborndata})

    if labexamsdata:
        data.append({'labexams': labexamsdata})

    if perehabilitationdata:
        data.append({'perehabilitation': perehabilitationdata})

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

    d = {'beginning_of_pregnancy':getdate(latest_beginning_of_pregnancy), 'expected_term':getdate(latest_expected_term), 'last_menstrual_period':getdate(latest_last_menstrual_period), 'date_time': getdate(date_time)}

    latest_date=max(d.iterkeys(), key = (lambda x: d[x]))

    if latest_date == 'date_time':
        last_pregnancy = frappe.get_all("Pregnancy", filters={"patient_record": patient_record, 'date_time': date_time})
    else:
        last_pregnancy = frappe.get_all("Pregnancy", filters={"patient_record": patient_record, latest_date: d[latest_date]})

    return last_pregnancy

def get_last_perineum_rehabilitation(patient_record):
    folders = frappe.get_all("Perineum Rehabilitation", filters={"patient_record": patient_record}, fields=["name", "modified"])

    if folders is not None:
        latest = max(folder.modified for folder in folders)

        latest_folder = frappe.get_all("Perineum Rehabilitation", filters={"patient_record": patient_record, 'modified': latest})

        return latest_folder

    else:
        return []

@frappe.whitelist()
def get_options(patient_record):
    dashboard = get_patient_dashboard(patient_record)

    result = []
    for attr, value in dashboard.__dict__.iteritems():
        if attr in DASHBOARD_LIST:
            label = dashboard.meta.get_label(attr)
            prev_value = dashboard.get(attr)

            result.append({"name": attr, "label": _(label), "value": prev_value})
            result = sorted(result)

    return result

@frappe.whitelist()
def update_dashboard(patient_record, options):
    options = json.loads(options)
    frappe.logger().debug(options)
    dashboard = frappe.get_doc("Custom Patient Record Dashboard", dict(patient_record=patient_record))

    if options:
        for option in options:
            for key, value in option.items():
                frappe.db.set_value("Custom Patient Record Dashboard", dict(patient_record=patient_record), key, value)
                frappe.db.commit()

    return "Success"
