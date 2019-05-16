# coding=utf-8

# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe
from frappe import _

def install(country=None):
	records = [
		{'doctype': 'Domain', 'domain': 'Sage-Femme'},

		# address template
		{'doctype':"Address Template", "country": country},

		# Profession
		{'doctype': 'Profession', 'profession_name': _('CEO')},
		{'doctype': 'Profession', 'profession_name': _('Manager')},
		{'doctype': 'Profession', 'profession_name': _('Analyst')},
		{'doctype': 'Profession', 'profession_name': _('Engineer')},
		{'doctype': 'Profession', 'profession_name': _('Accountant')},
		{'doctype': 'Profession', 'profession_name': _('Secretary')},
		{'doctype': 'Profession', 'profession_name': _('Associate')},
		{'doctype': 'Profession', 'profession_name': _('Administrative Officer')},
		{'doctype': 'Profession', 'profession_name': _('Business Development Manager')},
		{'doctype': 'Profession', 'profession_name': _('HR Manager')},
		{'doctype': 'Profession', 'profession_name': _('Project Manager')},
		{'doctype': 'Profession', 'profession_name': _('Head of Marketing and Sales')},
		{'doctype': 'Profession', 'profession_name': _('Software Developer')},
		{'doctype': 'Profession', 'profession_name': _('Designer')},
		{'doctype': 'Profession', 'profession_name': _('Researcher')},

		# Employment Status
		{'doctype': 'Employment Status', 'employee_type_name': _('Full-time')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Part-time')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Probation')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Contract')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Commission')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Piecework')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Intern')},
		{'doctype': 'Employment Status', 'employee_type_name': _('Apprentice')},

		# Addictions
		{'doctype': "Addiction", 'addictions': _("Tobacco")},
		{'doctype': "Addiction", 'addictions': _("Alcohol")},
		{'doctype': "Addiction", 'addictions': _("Cannabis")},
		{'doctype': "Addiction", 'addictions': _("Cocaine")},
		{'doctype': "Addiction", 'addictions': _("Psychoactive Drugs")},
		{'doctype': "Addiction", 'addictions': _("Heroin")},
		{'doctype': "Addiction", 'addictions': _("Methamphetamine/Ecstasy")},
		{'doctype': "Addiction", 'addictions': _("LSD/Ketamine/GHB")},
		{'doctype': "Addiction", 'addictions': _("Doping Substances")},
		{'doctype': "Addiction", 'addictions': _("Hallucinogenic Mushrooms")},
		{'doctype': "Addiction", 'addictions': _("Poppers/Glues and other Solvents")},

		# Allergies
		{'doctype': "Allergy", 'allergies': _("Latex")},
		{'doctype': "Allergy", 'allergies': _("Pollen")},
		{'doctype': "Allergy", 'allergies': _("Penicillin")},
		{'doctype': "Allergy", 'allergies': _("Iodine")},

		# Anesthesia Type
		{'doctype': "Anesthesia Type", 'anesthesia_type': _("General")},
		{'doctype': "Anesthesia Type", 'anesthesia_type': _("Local")},
		{'doctype': "Anesthesia Type", 'anesthesia_type': _("Rachianesthesia")},
		{'doctype': "Anesthesia Type", 'anesthesia_type': _("Peridural")},
		{'doctype': "Anesthesia Type", 'anesthesia_type': _("Pudendal Nerve")},

		# Birth Preparation Types
		{'doctype': "Birth Preparation Type", 'preparation_type': _("Classic")},
		{'doctype': "Birth Preparation Type", 'preparation_type': _("Prenatal Yoga")},
		{'doctype': "Birth Preparation Type", 'preparation_type': _("Sophrology")},
		{'doctype': "Birth Preparation Type", 'preparation_type': _("Hypnosis")},
		{'doctype': "Birth Preparation Type", 'preparation_type': _("Prenatal Singing")},

		# Contraception
		{'doctype': "Contraception", 'contraception': _("Optimizette")},
		{'doctype': "Contraception", 'contraception': _("Cerazette")},
		{'doctype': "Contraception", 'contraception': _("Microval")},
		{'doctype': "Contraception", 'contraception': _("Nexplanon")},
		{'doctype': "Contraception", 'contraception': _("Copper-Bearing IUD UT 380")},
		{'doctype': "Contraception", 'contraception': _("Copper-Bearing IUD UT 380 short")},
		{'doctype': "Contraception", 'contraception': _("Copper-Bearing IUD UT 380 standard")},
		{'doctype': "Contraception", 'contraception': _("Copper-Bearing IUD TT 380")},
		{'doctype': "Contraception", 'contraception': _("Copper-Bearing IUD Gynelle 375")},
		{'doctype': "Contraception", 'contraception': _("MIrena IUD")},
		{'doctype': "Contraception", 'contraception': _("Condom")},
		{'doctype': "Contraception", 'contraception': _("Withdrawal Method")},
		{'doctype': "Contraception", 'contraception': _("Leeloo G")},
		{'doctype': "Contraception", 'contraception': _("Lovavulo-Gé")},
		{'doctype': "Contraception", 'contraception': _("Optilova")},
		{'doctype': "Contraception", 'contraception': _("Optidril")},
		{'doctype': "Contraception", 'contraception': _("Minesse")},
		{'doctype': "Contraception", 'contraception': _("Melodia")},
		{'doctype': "Contraception", 'contraception': _("Yaz")},
		{'doctype': "Contraception", 'contraception': _("Jasmine")},
		{'doctype': "Contraception", 'contraception': _("Jasminelle")},
		{'doctype': "Contraception", 'contraception': _("CAYA Diaphragm")},
		{'doctype': "Contraception", 'contraception': _("FemCap 22mm Diameter")},
		{'doctype': "Contraception", 'contraception': _("FemCap 26mm Diameter")},
		{'doctype': "Contraception", 'contraception': _("FemCap 30mm Diameter")},
		{'doctype': "Contraception", 'contraception': _("Spermicides")},
		{'doctype': "Contraception", 'contraception': _("Ogino Method")},
		{'doctype': "Contraception", 'contraception': _("Standard Day Method")},
		{'doctype': "Contraception", 'contraception': _("Basal Body Temperature Method")},
		{'doctype': "Contraception", 'contraception': _("Billings Method")},
		{'doctype': "Contraception", 'contraception': _("Combined Indices Method")},

		# Delivery Way
		{'doctype': "Delivery Way", 'delivery_way': _("Normal"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Vacuum"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Forceps"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Spatulas"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Emergency C-Section"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Before Labour C-Section"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Therapeutic Abortion Sup To 22 WA"), 'used_in_parity': 1},
		{'doctype': "Delivery Way", 'delivery_way': _("Therapeutic Abortion Inf To 22 WA"), 'used_in_parity': 0},
		{'doctype': "Delivery Way", 'delivery_way': _("Surgical Abortion"), 'used_in_parity': 0},
		{'doctype': "Delivery Way", 'delivery_way': _("Drug Induced Abortion"), 'used_in_parity': 0},
		{'doctype': "Delivery Way", 'delivery_way': _("Miscarriage"), 'used_in_parity': 0},
		{'doctype': "Delivery Way", 'delivery_way': _("Ectopic Pregnancy"), 'used_in_parity': 0},

		# Placental Delivery
		{'doctype': "Placental Delivery", 'placental_delivery': _("Complete Normal Delivery")},
		{'doctype': "Placental Delivery", 'placental_delivery': _("Complete Directed Delivery")},
		{'doctype': "Placental Delivery", 'placental_delivery': _("Artificial Delivery")},
		{'doctype': "Placental Delivery", 'placental_delivery': _("Complete Manual Delivery")},
		{'doctype': "Placental Delivery", 'placental_delivery': _("Uterine Examination")},
		{'doctype': "Placental Delivery", 'placental_delivery': _("Incomplete Normal Delivery")},
		{'doctype': "Placental Delivery", 'placental_delivery': _("Incomplete Directed Delivery")},

		#Drugs
		{'doctype': "Drug", 'drug': _("Nexplanon Installation Kit")},
		{'doctype': "Drug", 'drug': _("Nexplanon Removal Kit")},
		{'doctype': "Drug", 'drug': _("IUD Installation Kit")},
		{'doctype': "Drug", 'drug': _("Povidone Iodine Skin Solution")},
		{'doctype': "Drug", 'drug': _("Povidone Iodine Vaginal Solution")},
		{'doctype': "Drug", 'drug': _("Speculum Size S")},
		{'doctype': "Drug", 'drug': _("Speculum Size M")},
		{'doctype': "Drug", 'drug': _("Speculum Size L")},
		{'doctype': "Drug", 'drug': _("Ibuprofen 400mg")},
		{'doctype': "Drug", 'drug': _("Spafon 160mg Lyoc")},
		{'doctype': "Drug", 'drug': _("Spasfon CP")},
		{'doctype': "Drug", 'drug': _("Spasfon 80mg Lyoc")},
		{'doctype': "Drug", 'drug': _("EMLA Patch")},
		{'doctype': "Drug", 'drug': _("Xylocain 2%")},
		{'doctype': "Drug", 'drug': _("CAYA Gel")},
		{'doctype': "Drug", 'drug': _("Double Breast-Pump Rent for Breastfeeding")},
		{'doctype': "Drug", 'drug': _("Breast-Pump Rent for Breastfeeding")},
		{'doctype': "Drug", 'drug': _("Optimizette")},
		{'doctype': "Drug", 'drug': _("Cerazette")},
		{'doctype': "Drug", 'drug': _("Microval")},
		{'doctype': "Drug", 'drug': _("Nexplanon")},
		{'doctype': "Drug", 'drug': _("Copper-Bearing IUD UT 380")},
		{'doctype': "Drug", 'drug': _("Copper-Bearing IUD UT 380 short")},
		{'doctype': "Drug", 'drug': _("Copper-Bearing IUD UT 380 standard")},
		{'doctype': "Drug", 'drug': _("Copper-Bearing IUD TT 380")},
		{'doctype': "Drug", 'drug': _("Copper-Bearing IUD Gynelle 375")},
		{'doctype': "Drug", 'drug': _("Mirena IUD")},
		{'doctype': "Drug", 'drug': _("Leeloo G")},
		{'doctype': "Drug", 'drug': _("Lovavulo-Ge")},
		{'doctype': "Drug", 'drug': _("Optilova")},
		{'doctype': "Drug", 'drug': _("Optidril")},
		{'doctype': "Drug", 'drug': _("Minesse")},
		{'doctype': "Drug", 'drug': _("Melodia")},
		{'doctype': "Drug", 'drug': _("Yaz")},
		{'doctype': "Drug", 'drug': _("Jasmine")},
		{'doctype': "Drug", 'drug': _("Jasminelle")},
		{'doctype': "Drug", 'drug': _("One ACL Rings System")},
		{'doctype': "Drug", 'drug': _("CAYA Diaphragm")},
		{'doctype': "Drug", 'drug': _("FemCap 22mm Diameter")},
		{'doctype': "Drug", 'drug': _("FemCap 26mm Diameter")},
		{'doctype': "Drug", 'drug': _("FemCap 30mm Diameter")},
		{'doctype': "Drug", 'drug': _("Spermicides")},
		{'doctype': "Drug", 'drug': _("Primperan 10mg")},
		{'doctype': "Drug", 'drug': _("Anausin 15mg LP")},
		{'doctype': "Drug", 'drug': _("Prokinyl 15mg LP")},
		{'doctype': "Drug", 'drug': _("Vogalen 15mg")},
		{'doctype': "Drug", 'drug': _("Vogalen 30mg")},
		{'doctype': "Drug", 'drug': _("Vogalen 7,5mg Lyoc")},
		{'doctype': "Drug", 'drug': _("Vogalen 5mg Suppository")},
		{'doctype': "Drug", 'drug': _("Maternov Nausea")},
		{'doctype': "Drug", 'drug': _("Gaviscon 10ml")},
		{'doctype': "Drug", 'drug': _("Maalox")},
		{'doctype': "Drug", 'drug': _("Omeprazole 10mg")},
		{'doctype': "Drug", 'drug': _("Omeprazole 20mg")},
		{'doctype': "Drug", 'drug': _("Ispagul Spagulax")},
		{'doctype': "Drug", 'drug': _("Parapsyllium")},
		{'doctype': "Drug", 'drug': _("Duphalac")},
		{'doctype': "Drug", 'drug': _("Transipeg")},
		{'doctype': "Drug", 'drug': _("Eductyl")},
		{'doctype': "Drug", 'drug': _("Microlax")},
		{'doctype': "Drug", 'drug': _("PhysioMat Belt")},
		{'doctype': "Drug", 'drug': _("Paracetamol 500mg")},
		{'doctype': "Drug", 'drug': _("MagneB6")},
		{'doctype': "Drug", 'drug': _("Thalamag")},
		{'doctype': "Drug", 'drug': _("Magnesium 300+")},
		{'doctype': "Drug", 'drug': _("Support Stocking - Class II")},
		{'doctype': "Drug", 'drug': _("Proctolog")},
		{'doctype': "Drug", 'drug': _("Titanorein")},
		{'doctype': "Drug", 'drug': _("Ultraproct")},
		{'doctype': "Drug", 'drug': _("Gynopevaryl LP")},
		{'doctype': "Drug", 'drug': _("Pevaryl Milk")},
		{'doctype': "Drug", 'drug': _("Flagyl 500mg")},
		{'doctype': "Drug", 'drug': _("Erginux")},
		{'doctype': "Drug", 'drug': _("Oligomax Fer")},
		{'doctype': "Drug", 'drug': _("Tardyferon B9")},
		{'doctype': "Drug", 'drug': _("Zyma D")},
		{'doctype': "Drug", 'drug': _("ErgyNatal Maternity")},

		#Lab Exam Types
		{'doctype': "Lab Exam Type", 'exam_type': _("Antiglobulin Testing"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("First Determination of ABO- and Rh-groups"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Second Determination of ABO- and Rh-groups"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Complete Blood"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Blood Platelets"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Ferritin"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("TP, TCA"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Fibrinogen"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("TSH"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("T3, T4"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Fasting Blood Glucose"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("HGPO 75g"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Total Cholesterol"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Triglycerides"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Glucosuria and Albuminuria"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("HCG Assay"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Albuminuria"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("ECBU +/- Antibiogram"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Proteinuria over 24h"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Vaginal Swab +/- Antibiogram"), 'default_value': 1},
		{'doctype': "Lab Exam Type", 'exam_type': _("Endocervix Swab"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Toxoplasmosis Serology"), 'default_value': 1},
		{'doctype': "Lab Exam Type", 'exam_type': _("Rubella Serology"), 'default_value': 1},
		{'doctype': "Lab Exam Type", 'exam_type': _("TPHA-VRDL Serology"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("HIV Serology"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("HBs Antigen"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Hp C Serology"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("CMV Serology"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Chickenpox Serology"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Ionograms"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("ASAT-ALAT"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("LDH"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Creatinemia"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Haptoglobin"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Bile Salts"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Total and Conjugated Bilirubin"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("Gamma-GT"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("PAL"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("CRP"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("HDL Cholesterol"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("LDL Cholesterol"), 'default_value': 0},
		{'doctype': "Lab Exam Type", 'exam_type': _("PAPP-A and Free Beta-HCG"), 'default_value': 0},

		# Surgical Interventions
		{'doctype': "Surgical Intervention", 'surgical_intervention': _("Wisdom Tooth Removal")},
		{'doctype': "Surgical Intervention", 'surgical_intervention': _("Appendicitis")},
		{'doctype': "Surgical Intervention", 'surgical_intervention': _("Tonsils Removal ")},
		{'doctype': "Surgical Intervention", 'surgical_intervention': _("Adenoids and Tonsils Removal")},
		{'doctype': "Surgical Intervention", 'surgical_intervention': _("Adenoids Removal")},

		# Echography Type
		{'doctype': "Echography Type", 'echography_type': _("Dating Ultrasound")},
		{'doctype': "Echography Type", 'echography_type': _("First Quarter Ultrasound")},
		{'doctype': "Echography Type", 'echography_type': _("Second Quarter Ultrasound")},
		{'doctype': "Echography Type", 'echography_type': _("Third Quarter Ultrasound")},
		{'doctype': "Echography Type", 'echography_type': _("Pelvic Ultrasound")},

		# Lab Exam Templates
		{'doctype': 'Lab Exam Template', 'title': _('6th Month Exam'), 'lab_exam_model': [{'exam_type': _('Glucosuria and Albuminuria')}, {'exam_type': _('Toxoplasmosis Serology')}, {'exam_type': _('Antiglobulin Testing')}, {'exam_type': _('Complete Blood')}]},
		{'doctype': 'Lab Exam Template', 'title': _('5th Month Exam'), 'lab_exam_model': [{'exam_type': _('Glucosuria and Albuminuria')}, {'exam_type': _('Toxoplasmosis Serology')}, {'exam_type': _('HGPO 75g')}]},
		{'doctype': 'Lab Exam Template', 'title': _('1st Month Exam'), 'lab_exam_model': [{'exam_type': _('Fasting Blood Glucose')}, {'exam_type': _('PAPP-A and Free Beta-HCG')}, {'exam_type': _('Complete Blood')}, {'exam_type': _('HBs Antigen')},
			{'exam_type': _('Ferritin')}, {'exam_type': _('Hp C Serology')}, {'exam_type': _('HIV Serology')}, {'exam_type': _('Rubella Serology')}, {'exam_type': _('Toxoplasmosis Serology')}, {'exam_type': _('First Determination of ABO- and Rh-groups')},
			{'exam_type': _('Second Determination of ABO- and Rh-groups')}, {'exam_type': _('Antiglobulin Testing')}, {'exam_type': _('TPHA-VRDL Serology')}, {'exam_type': _('Glucosuria and Albuminuria')}]},
		{'doctype': 'Lab Exam Template', 'title': _('Standard Exam'), 'lab_exam_model': [{'exam_type': _('Glucosuria and Albuminuria')}, {'exam_type': _('Toxoplasmosis Serology')}]},
	]

	from frappe.modules import scrub
	for r in records:
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

def codifications():
	records = [
		# Midwife Codifications
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire','codification': 'C', 'basic_price': 23, 'billing_price': 23, 'codification_name': 'C', 'codification_description': 'Consultation'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'V', 'basic_price': 23, 'billing_price': 23, 'codification_name': 'V', 'codification_description': 'Visite'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF', 'basic_price': 2.80, 'billing_price': 2.80, 'codification_name': 'SF', 'codification_description': 'Actes en SF'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'HN', 'basic_price': 0, 'billing_price': 0, 'codification_name': 'HN', 'codification_description': 'Actes Hors Nomenclature'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 15', 'basic_price': 42, 'billing_price': 42, 'codification_name': 'SF 15', 'codification_description': 'PNP: Première séance entretien individuel | Sur prescription à domicile: Grossesse unique avec monitoring à partir de 24 sem'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 11,6', 'basic_price': 32.48, 'billing_price': 32.48, 'codification_name': 'SF 11,6', 'codification_description': 'PNP: 7 séances suivantes ≤ 3 femmes'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 12', 'basic_price': 33.60, 'billing_price': 33.60, 'codification_name': 'SF 12', 'codification_description': 'PNP: 7 séances suivantes individuelles'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 16,5', 'basic_price': 46.20, 'billing_price': 46.20, 'codification_name': 'SF 16,5', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J12 (J0 étant le jour de l\'accouchement): Un enfant, les 2 premiers forfaits'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 23', 'basic_price': 64.40, 'billing_price': 64.40, 'codification_name': 'SF 23', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J12 (J0 étant le jour de l\'accouchement): Deux enfants et plus, les 2 premiers forfaits'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 17', 'basic_price': 47.60, 'billing_price': 47.60, 'codification_name': 'SF 17', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J12 (J0 étant le jour de l\'accouchement): Deux enfants et plus, les forfaits suivants'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 7', 'basic_price': 19.60, 'billing_price': 19.60, 'codification_name': 'SF 7', 'codification_description': 'Rééducation périnéo-sphinctérienne'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 9', 'basic_price': 25.20, 'billing_price': 25.20, 'codification_name': 'SF 9', 'codification_description': 'Sur prescription à domicile: Surveillance grossesse sans monitoring'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JKLD001', 'basic_price': 38.40, 'billing_price': 38.40, 'codification_name': 'JKLD001', 'codification_description': 'Pose d\'un dispositif intra-utérin'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'QZLA004', 'basic_price': 17.99, 'billing_price': 17.99, 'codification_name': 'QZLA004', 'codification_description': 'Pose d\'implant pharmacologique sous-cutané'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'QZGA002', 'basic_price': 41.80, 'billing_price': 41.80, 'codification_name': 'QZGA002', 'codification_description': 'Ablation ou changement d\'implant pharmacologique sous-cutané'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JKHD001', 'basic_price': 12.46, 'billing_price': 12.46, 'codification_name': 'JKHD001', 'codification_description': 'Prélèvement cervicovaginal'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 6', 'basic_price': 16.80, 'billing_price': 16.80, 'codification_name': 'SF 6', 'codification_description': 'PNP: 7 séances > 3 femmes (max = 6 )'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 22', 'basic_price': 61.60, 'billing_price': 61.60, 'codification_name': 'SF 22', 'codification_description': 'Sur prescription à domicile: Grossesse multiple avec monitoring à partir de 24 sem'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 19', 'basic_price': 53.20, 'billing_price': 53.20, 'codification_name': 'SF 19', 'codification_description': 'Sur prescription au cabinet: Grossesse multiple avec monitoring à partir de 24 sem'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SP', 'basic_price': 18.55, 'billing_price': 18.55, 'codification_name': 'SP', 'codification_description': 'Séances post-natales (2 séances du 8e jour qui suit l\'accouchement à la CS post-natale)'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 22,4', 'basic_price': 62.72, 'billing_price': 62.72, 'codification_name': 'SF 22,4', 'codification_description': 'Ablation DIU par un matériel intra-utérin de préhension par voie vaginale'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JKKD001', 'basic_price': 38.40, 'billing_price': 38.40, 'codification_name': 'JKKD001', 'codification_description': 'Changement d\'un dispositif intra-utérin'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JLLD001', 'basic_price': 0, 'billing_price': 0, 'codification_name': 'JLLD001', 'codification_description': 'Pose de dispositif intra-vaginal'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JLGD001', 'basic_price': 0, 'billing_price': 0, 'codification_name': 'JLGD001', 'codification_description': 'Ablation ou changement de dispositif intra-vaginal'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQM007', 'basic_price': 37.80, 'billing_price': 37.80, 'codification_name': 'ZCQM007', 'codification_description': 'Échographie du petit bassin [pelvis] féminin pour surveillance de l\'ovulation'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQM009', 'basic_price': 42.25, 'billing_price': 42.25, 'codification_name': 'ZCQM009', 'codification_description': 'Échographie-doppler du petit bassin [pelvis] féminin pour surveillance de l\'ovulation'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire','codification': 'JNQM001', 'basic_price': 35.65, 'billing_price': 35.65, 'codification_name': 'JNQM001', 'codification_description': 'Échographie non morphologique de la grossesse avant 11 semaines d\'aménorrhée'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM010', 'basic_price': 61.47, 'billing_price': 61.47, 'codification_name': 'JQQM010', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse uniembryonnaire au 1er trimestre'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM015', 'basic_price': 71.57, 'billing_price': 71.57, 'codification_name': 'JQQM015', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse multiembryonnaire au 1er trimestre'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM018', 'basic_price': 100.20, 'billing_price': 100.20, 'codification_name': 'JQQM018', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse unifœtale au 2ème trimestre'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM016', 'basic_price': 100.20, 'billing_price': 100.20, 'codification_name': 'JQQM016', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse unifœtale au 3ème trimestre'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM019', 'basic_price': 154.09, 'billing_price': 154.09, 'codification_name': 'JQQM019', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse multifœtale au 2ème trimestre'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM017', 'basic_price': 154.09, 'billing_price': 154.09, 'codification_name': 'JQQM017', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse multifœtale au 3ème trimestre'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM002', 'basic_price': 92.19, 'billing_price': 92.19, 'codification_name': 'JQQM002', 'codification_description': 'Échographie d\'une grossesse unifœtale à partir du 2ème trimestre avec échographie-doppler des artères utérines de la mère et des vaisseaux du fœtus, pour souffrance fœtale'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM007', 'basic_price': 133.81, 'billing_price': 133.81, 'codification_name': 'JQQM007', 'codification_description': 'Échographie d\'une grossesse multifœtale à partir du 2ème trimestre avec échographie-doppler des artères utérines de la mère et des vaisseaux des fœtus, pour souffrance fœtale'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM001', 'basic_price': 46.15, 'billing_price': 46.15, 'codification_name': 'JQQM001', 'codification_description': 'Échographie de surveillance de la croissance fœtale'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'JQQM003', 'basic_price': 75.60, 'billing_price': 75.60, 'codification_name': 'JQQM003', 'codification_description': 'Échographie de surveillance de la croissance fœtale avec échographie-doppler des artères utérines de la mère et des vaisseaux du fœtus'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'IF', 'basic_price': 4, 'billing_price': 4, 'codification_name': 'IF', 'codification_description': 'Indemnité forfaitaire de déplacement', 'lump_sum_travel_allowance': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'IK', 'basic_price': 0.45, 'billing_price': 0.45, 'codification_name': 'IK_Plaine', 'codification_description': 'Indemnité kilométrique plaine', 'mileage_allowance_lowland': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'IK', 'basic_price': 0.73, 'billing_price': 0.73, 'codification_name': 'IK_Montagne', 'codification_description': 'Indemnité kilométrique montagne', 'mileage_allowance_mountain': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'IK', 'basic_price': 3.95, 'billing_price': 3.95, 'codification_name': 'IK_Pied_Ski', 'codification_description': 'Indemnité kilométrique à pied ou à ski', 'mileage_allowance_walking_skiing': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'P', 'basic_price': 35, 'billing_price': 35, 'codification_name': 'P', 'codification_description': 'Indemnité de nuit de 20h à 0h et de 6h à 8h (appel à partir de 19h)', 'night_work_allowance_1': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'S', 'basic_price': 40, 'billing_price': 40, 'codification_name': 'S', 'codification_description': 'Indemnité de nuit de 0h à 6h', 'night_work_allowance_2': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'F', 'basic_price': 21, 'billing_price': 21, 'codification_name': 'F', 'codification_description': 'Indemnité dimanche et jours fériés, en cas d\'urgence dès samedi 12h', 'sundays_holidays_allowance': 1},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'C + JKHD001', 'basic_price': 35.46, 'billing_price': 35.46, 'codification_name': 'C + JKHD001', 'codification_description': 'Consultation + Prélèvement Cervicovaginal'},
		# 02/2019
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'C + MSF', 'basic_price': 25, 'billing_price': 25, 'codification_name': 'C + MSF', 'codification_description': 'Consultation + Majoration'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'V + MSF', 'basic_price': 25, 'billing_price': 25, 'codification_name': 'V + MSF', 'codification_description': 'Visite + Majoration'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 12,6', 'basic_price': 35.28, 'billing_price': 35.28, 'codification_name': 'SF 12,6', 'codification_description': 'Bilan prénatal valorisant la prévention et le parcours de soins (1 séance)'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 15,6', 'basic_price': 43.68, 'billing_price': 43.68, 'codification_name': 'SF 15,6', 'codification_description': 'Surveillance de grossesse pathologique simple + RCF à partir de 24SA'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 22,6', 'basic_price': 63.28, 'billing_price': 63.28, 'codification_name': 'SF 22,6', 'codification_description': 'Surveillance de grossesse pathologique multiple + RCF à partir de 24SA'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 12,5', 'basic_price': 35, 'billing_price': 35, 'codification_name': 'SF 12,5', 'codification_description': 'Examen de grossesse simple à partir de la 24ème SA comportant RCF+CR'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'SF 19,5', 'basic_price': 54.6, 'billing_price': 54.6, 'codification_name': 'SF 19,5', 'codification_description': 'Examen de grossesse multiple à partir de la 24ème SA comportant RCF+CR'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'DSP', 'basic_price': 25, 'billing_price': 25, 'codification_name': 'DSP', 'codification_description': 'Majoration forfaitaire sorties précoces (sur la 1e visite si dans les 24h après la sortie et si à moins de 72h de l’accouchement)'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'CCP', 'basic_price': 46, 'billing_price': 46, 'codification_name': 'CCP', 'codification_description': 'Première consultation de contraception et de prévention des jeunes filles entre 15 et 18 ans'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQJ001', 'basic_price': 69.93, 'billing_price': 69.93, 'codification_name': 'ZCQJ001', 'codification_description': 'Echographie-doppler transcutanée et échographie-doppler par voie rectale et/ou vaginale [par voie cavitaire] du petit bassin [pelvis] féminin'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQJ002', 'basic_price': 69.93, 'billing_price': 69.93, 'codification_name': 'ZCQJ002', 'codification_description': 'Échographie-doppler du petit bassin [pelvis] féminin, par voie rectale et/ou vaginale [par voie cavitaire]'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQJ003', 'basic_price': 52.45, 'billing_price': 52.45, 'codification_name': 'ZCQJ003', 'codification_description': 'Échographie du petit bassin [pelvis] féminin, par voie rectale et/ou vaginale [par voie cavitaire]'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQJ006', 'basic_price': 56.7, 'billing_price': 56.7, 'codification_name': 'ZCQJ006', 'codification_description': 'Echographie transcutanée avec échographie par voie rectale et/ou vaginale [par voie cavitaire] du petit bassin [pelvis] féminin'},
		{'doctype': 'Codification', 'accounting_item': 'Recettes encaissées, Honoraire', 'codification': 'ZCQM003', 'basic_price': 52.45, 'billing_price': 52.45, 'codification_name': 'ZCQM003', 'codification_description': 'Échographie transcutanée du petit bassin [pelvis] féminin'}
	]

	from frappe.modules import scrub
	for r in records:
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise
