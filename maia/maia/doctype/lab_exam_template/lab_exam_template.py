# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabExamTemplate(Document):
	pass

@frappe.whitelist()
def get_lab_exam_template(lab_exam_template):
	template = frappe.get_doc('Lab Exam Template', {'name': lab_exam_template})
	return template.lab_exam_model
