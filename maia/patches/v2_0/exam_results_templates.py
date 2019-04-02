# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


def execute():
	language = frappe.get_single("System Settings").language
	frappe.local.lang = language

	if frappe.db.exists("Lab Exam Type", "PAPP-A and Free Beta-HCG"):
		try:
			frappe.rename_doc("Lab Exam Type", "PAPP-A and Free Beta-HCG", _("PAPP-A and Free Beta-HCG"))
			frappe.db.commit()
		except Exception as e:
			print(e)

	if frappe.db.exists("Lab Exam Type", "Première Déterminationd de Groupe Sanguin Rhésus Phénotypé"):
		try:
			frappe.rename_doc("Lab Exam Type", "Première Déterminationd de Groupe Sanguin Rhésus Phénotypé", _("First Determination of ABO- and Rh-groups"))
			frappe.db.commit()
		except Exception as e:
			print(e)

	if frappe.db.exists("Lab Exam Type", "Deuxième Déterminationd de Groupe Sanguin Rhésus Phénotypé"):
		try:
			frappe.rename_doc("Lab Exam Type", "Deuxième Déterminationd de Groupe Sanguin Rhésus Phénotypé", _("Second Determination of ABO- and Rh-groups"))
			frappe.db.commit()
		except Exception as e:
			print(e)


	records = [
	{'doctype': 'Lab Exam Template', 'title': _('6th Month Exam'), 'lab_exam_model': [{'exam_type': _('Glucosuria and Albuminuria')}, {'exam_type': _('HBs Antigen')}, {'exam_type': _('Toxoplasmosis Serology')}, {'exam_type': _('Antiglobulin Testing')}, {'exam_type': _('Complete Blood')}]},
	{'doctype': 'Lab Exam Template', 'title': _('5th Month Exam'), 'lab_exam_model': [{'exam_type': _('Glucosuria and Albuminuria')}, {'exam_type': _('Toxoplasmosis Serology')}, {'exam_type': _('HGPO 75g')}]},
	{'doctype': 'Lab Exam Template', 'title': _('1st Month Exam'), 'lab_exam_model': [{'exam_type': _('Fasting Blood Glucose')}, {'exam_type': _('PAPP-A and Free Beta-HCG')}, {'exam_type': _('Complete Blood')},
		{'exam_type': _('Ferritin')}, {'exam_type': _('Hp C Serology')}, {'exam_type': _('HIV Serology')}, {'exam_type': _('Rubella Serology')}, {'exam_type': _('Toxoplasmosis Serology')}, {'exam_type': _('First Determination of ABO- and Rh-groups')},
		{'exam_type': _('Second Determination of ABO- and Rh-groups')}, {'exam_type': _('Antiglobulin Testing')}, {'exam_type': _('TPHA-VRDL Serology')}, {'exam_type': _('Glucosuria and Albuminuria')}]},
	{'doctype': 'Lab Exam Template', 'title': _('Standard Exam'), 'lab_exam_model': [{'exam_type': _('Glucosuria and Albuminuria')}, {'exam_type': _('Toxoplasmosis Serology')}]},
	]

	from frappe.modules import scrub
	for r in records:
		for s in r['lab_exam_model']:
			subdoc = frappe.new_doc("Lab Exam Type")
			subdoc.exam_type = s['exam_type']
			try:
				subdoc.insert(ignore_permissions=True)
				print(subdoc.name)
			except frappe.DuplicateEntryError as e:
				# pass DuplicateEntryError and continue
				if e.args and e.args[0]==subdoc.doctype and e.args[1]==subdoc.name:
					# make sure DuplicateEntryError is for the exact same doc and not a related doc
					pass
				else:
					raise
		print(r)
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==subdoc.doctype and e.args[1]==subdoc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise
