# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
    lab_exams = frappe.get_all("Lab Exam Type")

    default_list = ["Sérologie Rubéole", "Sérologie Toxoplasmose", "Prélèvement vaginal +/- Antibiogramme"]

    for exam in lab_exams:
        if exam.name in default_list:
            frappe.db.set_value("Lab Exam Type", exam.name, "default_value", 1)

    frappe.db.commit()
