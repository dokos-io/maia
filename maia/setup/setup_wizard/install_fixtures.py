# coding=utf-8

# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe

from frappe import _

default_lead_sources = ["Existing Customer", "Reference", "Advertisement",
	"Cold Calling", "Exhibition", "Supplier Reference", "Mass Mailing",
	"Customer's Vendor", "Campaign", "Walk In"]

def install(country=None):
	records = [
		#setup domain
		{ 'doctype': 'Domain', 'domain': 'Sage-Femme'},

		# address template
		{'doctype':"Address Template", "country": country},

		# item group
		{'doctype': 'Item Group', 'item_group_name': _('All Item Groups'), 'is_group': 1, 'parent_item_group': ''},
		{'doctype': 'Item Group', 'item_group_name': _('Selling'), 'is_group': 1, 'parent_item_group': _('All Item Groups')},
		{'doctype': 'Item Group', 'item_group_name': _('Codifications'), 'is_group': 0, 'parent_item_group': _('Selling') },
		{'doctype': 'Item Group', 'item_group_name': _('Buying'), 'is_group': 1, 'parent_item_group': _('All Item Groups')},
		{'doctype': 'Item Group', 'item_group_name': _('Purchases'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Rental Expenses'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Furniture and Equipment Rental'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Maintenance and Repair'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Temporary Staff'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Small Equipment'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Heating, Water, Gaz, Electricity'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Fees without Retrocession'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Insurance Premium'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Vehicule Expenses'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Other Travel Related Costs'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Personal Social Security Contributions'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Reception and Representation Expenses'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Office Supplies, Documentation, Post Office'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Deeds and Litigation Costs'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Professional Organizations Contributions'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Miscellaneous Management Expenses'), 'is_group': 0, 'parent_item_group': _('Buying') },
		{'doctype': 'Item Group', 'item_group_name': _('Financial Expenses'), 'is_group': 0, 'parent_item_group': _('Buying') },

		# salary component
		{'doctype': 'Salary Component', 'salary_component': _('Income Tax'), 'description': _('Income Tax'), 'type': 'Deduction'},
		{'doctype': 'Salary Component', 'salary_component': _('Basic'), 'description': _('Basic'), 'type': 'Earning'},
		{'doctype': 'Salary Component', 'salary_component': _('Arrear'), 'description': _('Arrear'), 'type': 'Earning'},
		{'doctype': 'Salary Component', 'salary_component': _('Leave Encashment'), 'description': _('Leave Encashment'), 'type': 'Earning'},


		# expense claim type
		{'doctype': 'Expense Claim Type', 'name': _('Calls'), 'expense_type': _('Calls')},
		{'doctype': 'Expense Claim Type', 'name': _('Food'), 'expense_type': _('Food')},
		{'doctype': 'Expense Claim Type', 'name': _('Medical'), 'expense_type': _('Medical')},
		{'doctype': 'Expense Claim Type', 'name': _('Others'), 'expense_type': _('Others')},
		{'doctype': 'Expense Claim Type', 'name': _('Travel'), 'expense_type': _('Travel')},

		# leave type
		{'doctype': 'Leave Type', 'leave_type_name': _('Casual Leave'), 'name': _('Casual Leave'),
			'is_encash': 1, 'is_carry_forward': 1, 'max_days_allowed': '3', 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Compensatory Off'), 'name': _('Compensatory Off'),
			'is_encash': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Sick Leave'), 'name': _('Sick Leave'),
			'is_encash': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Privilege Leave'), 'name': _('Privilege Leave'),
			'is_encash': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': _('Leave Without Pay'), 'name': _('Leave Without Pay'),
			'is_encash': 0, 'is_carry_forward': 0, 'is_lwp':1, 'include_holiday': 1},

		# Employment Type
		{'doctype': 'Employment Type', 'employee_type_name': _('Full-time')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Part-time')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Probation')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Contract')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Commission')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Piecework')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Intern')},
		{'doctype': 'Employment Type', 'employee_type_name': _('Apprentice')},

		# Department
		{'doctype': 'Department', 'department_name': _('Accounts')},
		{'doctype': 'Department', 'department_name': _('Marketing')},
		{'doctype': 'Department', 'department_name': _('Sales')},
		{'doctype': 'Department', 'department_name': _('Purchase')},
		{'doctype': 'Department', 'department_name': _('Operations')},
		{'doctype': 'Department', 'department_name': _('Production')},
		{'doctype': 'Department', 'department_name': _('Dispatch')},
		{'doctype': 'Department', 'department_name': _('Customer Service')},
		{'doctype': 'Department', 'department_name': _('Human Resources')},
		{'doctype': 'Department', 'department_name': _('Management')},
		{'doctype': 'Department', 'department_name': _('Quality Management')},
		{'doctype': 'Department', 'department_name': _('Research & Development')},
		{'doctype': 'Department', 'department_name': _('Legal')},

		# Designation
		{'doctype': 'Designation', 'designation_name': _('CEO')},
		{'doctype': 'Designation', 'designation_name': _('Manager')},
		{'doctype': 'Designation', 'designation_name': _('Analyst')},
		{'doctype': 'Designation', 'designation_name': _('Engineer')},
		{'doctype': 'Designation', 'designation_name': _('Accountant')},
		{'doctype': 'Designation', 'designation_name': _('Secretary')},
		{'doctype': 'Designation', 'designation_name': _('Associate')},
		{'doctype': 'Designation', 'designation_name': _('Administrative Officer')},
		{'doctype': 'Designation', 'designation_name': _('Business Development Manager')},
		{'doctype': 'Designation', 'designation_name': _('HR Manager')},
		{'doctype': 'Designation', 'designation_name': _('Project Manager')},
		{'doctype': 'Designation', 'designation_name': _('Head of Marketing and Sales')},
		{'doctype': 'Designation', 'designation_name': _('Software Developer')},
		{'doctype': 'Designation', 'designation_name': _('Designer')},
		{'doctype': 'Designation', 'designation_name': _('Researcher')},

		# territory
		{'doctype': 'Territory', 'territory_name': _('All Territories'), 'is_group': 1, 'name': _('All Territories'), 'parent_territory': ''},

		# customer group
		{'doctype': 'Customer Group', 'customer_group_name': _('All Customer Groups'), 'is_group': 1, 	'name': _('All Customer Groups'), 'parent_customer_group': ''},
		{'doctype': 'Customer Group', 'customer_group_name': _('Individual'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': _('Commercial'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': _('Non Profit'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': _('Government'), 'is_group': 0, 'parent_customer_group': _('All Customer Groups')},

		# supplier type
		{'doctype': 'Supplier Type', 'supplier_type': _('Supplies')},
		{'doctype': 'Supplier Type', 'supplier_type': _('Supermarket')},
		{'doctype': 'Supplier Type', 'supplier_type': _('Restaurant')},
		{'doctype': 'Supplier Type', 'supplier_type': _('Transport and Travel')},
		{'doctype': 'Supplier Type', 'supplier_type': _('Miscellaneous')},
		{'doctype': 'Supplier Type', 'supplier_type': _('Pharmaceutical')},

		# Sales Person
		{'doctype': 'Sales Person', 'sales_person_name': _('Sales Team'), 'is_group': 1, "parent_sales_person": ""},

		# UOM
		{'uom_name': _('Unit'), 'doctype': 'UOM', 'name': _('Unit'), "must_be_whole_number": 1},
		{'uom_name': _('Box'), 'doctype': 'UOM', 'name': _('Box'), "must_be_whole_number": 1},
		{'uom_name': _('Kg'), 'doctype': 'UOM', 'name': _('Kg')},
		{'uom_name': _('Meter'), 'doctype': 'UOM', 'name': _('Meter')},
		{'uom_name': _('Litre'), 'doctype': 'UOM', 'name': _('Litre')},
		{'uom_name': _('Gram'), 'doctype': 'UOM', 'name': _('Gram')},
		{'uom_name': _('Nos'), 'doctype': 'UOM', 'name': _('Nos'), "must_be_whole_number": 1},
		{'uom_name': _('Pair'), 'doctype': 'UOM', 'name': _('Pair'), "must_be_whole_number": 1},
		{'uom_name': _('Set'), 'doctype': 'UOM', 'name': _('Set'), "must_be_whole_number": 1},
		{'uom_name': _('Hour'), 'doctype': 'UOM', 'name': _('Hour')},
		{'uom_name': _('Minute'), 'doctype': 'UOM', 'name': _('Minute')},
		{'uom_name': _('Month'), 'doctype': 'UOM', 'name': _('Minute')},

		# Mode of Payment
		{'doctype': 'Mode of Payment', 'mode_of_payment': 'Check' if country=="United States" else _('Cheque'), 'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Cash'), 'type': 'Cash'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Credit Card'), 'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': _('Wire Transfer'), 'type': 'Bank'},

		# Activity Type
		{'doctype': 'Activity Type', 'activity_type': _('Planning')},
		{'doctype': 'Activity Type', 'activity_type': _('Research')},
		{'doctype': 'Activity Type', 'activity_type': _('Proposal Writing')},
		{'doctype': 'Activity Type', 'activity_type': _('Execution')},
		{'doctype': 'Activity Type', 'activity_type': _('Communication')},

		# Lead Source
		{'doctype': "Item Attribute", "attribute_name": _("Size"), "item_attribute_values": [
			{"attribute_value": _("Extra Small"), "abbr": "XS"},
			{"attribute_value": _("Small"), "abbr": "S"},
			{"attribute_value": _("Medium"), "abbr": "M"},
			{"attribute_value": _("Large"), "abbr": "L"},
			{"attribute_value": _("Extra Large"), "abbr": "XL"}
		]},

		{'doctype': "Item Attribute", "attribute_name": _("Colour"), "item_attribute_values": [
			{"attribute_value": _("Red"), "abbr": "RED"},
			{"attribute_value": _("Green"), "abbr": "GRE"},
			{"attribute_value": _("Blue"), "abbr": "BLU"},
			{"attribute_value": _("Black"), "abbr": "BLA"},
			{"attribute_value": _("White"), "abbr": "WHI"}
		]},

		{'doctype': "Email Account", "email_id": "sales@example.com", "append_to": "Opportunity"},
		{'doctype': "Email Account", "email_id": "support@example.com", "append_to": "Issue"},
		{'doctype': "Email Account", "email_id": "jobs@example.com", "append_to": "Job Applicant"},

		{'doctype': "Party Type", "party_type": "Customer"},
		{'doctype': "Party Type", "party_type": "Supplier"},
		{'doctype': "Party Type", "party_type": "Employee"},

		{"doctype": "Offer Term", "offer_term": _("Date of Joining")},
		{"doctype": "Offer Term", "offer_term": _("Annual Salary")},
		{"doctype": "Offer Term", "offer_term": _("Probationary Period")},
		{"doctype": "Offer Term", "offer_term": _("Employee Benefits")},
		{"doctype": "Offer Term", "offer_term": _("Working Hours")},
		{"doctype": "Offer Term", "offer_term": _("Stock Options")},
		{"doctype": "Offer Term", "offer_term": _("Department")},
		{"doctype": "Offer Term", "offer_term": _("Job Description")},
		{"doctype": "Offer Term", "offer_term": _("Responsibilities")},
		{"doctype": "Offer Term", "offer_term": _("Leaves per Year")},
		{"doctype": "Offer Term", "offer_term": _("Notice Period")},
		{"doctype": "Offer Term", "offer_term": _("Incentives")},

		{'doctype': "Print Heading", 'print_heading': _("Credit Note")},
		{'doctype': "Print Heading", 'print_heading': _("Debit Note")},

		# Assessment Group
		{'doctype': 'Assessment Group', 'assessment_group_name': _('All Assessment Groups'),
			'is_group': 1, 'parent_assessment_group': ''},

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
		{'doctype': "Delivery Way", 'delivery_way': _("Normal")},
		{'doctype': "Delivery Way", 'delivery_way': _("Vacuum")},
		{'doctype': "Delivery Way", 'delivery_way': _("Forceps")},
		{'doctype': "Delivery Way", 'delivery_way': _("Spatulas")},
		{'doctype': "Delivery Way", 'delivery_way': _("Emergency C-Section")},
		{'doctype': "Delivery Way", 'delivery_way': _("Before Labour C-Section")},

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
		{'doctype': "Lab Exam Type", 'exam_type': _("Antiglobulin Testing")},
		{'doctype': "Lab Exam Type", 'exam_type': _("First Determination of ABO- and Rh-groups")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Second Determination of ABO- and Rh-groups")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Complete Blood")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Blood Platelets")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Ferritin")},
		{'doctype': "Lab Exam Type", 'exam_type': _("TP, TCA")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Fibrinogen")},
		{'doctype': "Lab Exam Type", 'exam_type': _("TSH")},
		{'doctype': "Lab Exam Type", 'exam_type': _("T3, T4")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Fasting Blood Glucose")},
		{'doctype': "Lab Exam Type", 'exam_type': _("HGPO 75g")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Total Cholesterol")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Triglycerides")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Glucosuria and Albuminuria")},
		{'doctype': "Lab Exam Type", 'exam_type': _("HCG Assay")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Albuminuria")},
		{'doctype': "Lab Exam Type", 'exam_type': _("ECBU +/- Antibiogram")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Proteinuria over 24h")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Vaginal Swab +/- Antibiogram")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Endocervix Swab")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Toxoplasmosis Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Rubella Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("TPHA-VRDL Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("HIV Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("HBs Antigen")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Hp C Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("CMV Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Chickenpox Serology")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Ionograms")},
		{'doctype': "Lab Exam Type", 'exam_type': _("ASAT-ALAT")},
		{'doctype': "Lab Exam Type", 'exam_type': _("LDH")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Creatinemia")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Haptoglobin")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Bile Salts")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Total and Conjugated Bilirubin")},
		{'doctype': "Lab Exam Type", 'exam_type': _("Gamma-GT")},
		{'doctype': "Lab Exam Type", 'exam_type': _("PAL")},
		{'doctype': "Lab Exam Type", 'exam_type': _("CRP")},
		{'doctype': "Lab Exam Type", 'exam_type': _("HDL Cholesterol")},
		{'doctype': "Lab Exam Type", 'exam_type': _("LDL Cholesterol")},
		{'doctype': "Lab Exam Type", 'exam_type': _("PAPP-A and Free Beta-HCG")},

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
	]


	from erpnext.setup.setup_wizard.data.industry_type import get_industry_types
	records += [{"doctype":"Industry Type", "industry": d} for d in get_industry_types()]
	# records += [{"doctype":"Operation", "operation": d} for d in get_operations()]

	records += [{'doctype': 'Lead Source', 'source_name': _(d)} for d in default_lead_sources]

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
		except frappe.DuplicateEntryError, e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

def purchase_items(country=None):
	records = [
		{'doctype': 'Item', 'item_code': _('Exam Sheets'), 'item_name': _('Exam Sheets'), 'item_group': _('Purchases'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Medical Equipment'), 'item_name': _('Medical Equipment'), 'item_group': _('Purchases'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Disposable Equipment'), 'item_name': _('Disposable Equipment'), 'item_group': _('Purchases'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Rent'), 'item_name': _('Rent'), 'item_group': _('Rental Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Rental Expense'), 'item_name': _('Rental Expense'), 'item_group': _('Rental Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Collaboration Fee'), 'item_name': _('Collaboration Fee'), 'item_group': _('Furniture and Equipment Rental'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Finance Lease Rent'), 'item_name': _('Finance Lease Rent'), 'item_group': _('Furniture and Equipment Rental'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Duty paid to an Hospital or Clinic'), 'item_name': _('Duty paid to an Hospital or Clinic'), 'item_group': _('Furniture and Equipment Rental'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Maintenance and Repair Expenses'), 'item_name': _('Maintenance and Repair Expenses'), 'item_group': _('Maintenance and Repair'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Laundering Expenses'), 'item_name': _('Laundering Expenses'), 'item_group': _('Maintenance and Repair'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Temporary Staff Expenses'), 'item_name': _('Temporary Staff Expenses'), 'item_group': _('Temporary Staff'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Small Material'), 'item_name': _('Small Material'), 'item_group': _('Small Equipment'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Software'), 'item_name': _('Software'), 'item_group': _('Small Equipment'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Office Furniture'), 'item_name': _('Office Furniture'), 'item_group': _('Small Equipment'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Clothing Expenses'), 'item_name': _('Clothing Expenses'), 'item_group': _('Small Equipment'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Heating'), 'item_name': _('Heating'), 'item_group': _('Heating, Water, Gaz, Electricity'), 'stock_uom': _('Month'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Water'), 'item_name': _('Water'), 'item_group': _('Heating, Water, Gaz, Electricity'), 'stock_uom': _('Month'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Gaz'), 'item_name': _('Gaz'), 'item_group': _('Heating, Water, Gaz, Electricity'), 'stock_uom': _('Month'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Electricity'), 'item_name': _('Electricity'), 'item_group': _('Heating, Water, Gaz, Electricity'), 'stock_uom': _('Month'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Fees paid to professionals other than peers'), 'item_name': _('Fees paid to professionals other than peers'), 'item_group': _('Fees without Retrocession'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Remuneration for complementary services'), 'item_name': _('Remuneration for complementary services'), 'item_group': _('Fees without Retrocession'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Deductible Premium'), 'item_name': _('Deductible Premium'), 'item_group': _('Insurance Premium'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Non Deductible Premium'), 'item_name': _('Non Deductible Premium'), 'item_group': _('Insurance Premium'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Vehicule Expense'), 'item_name': _('Vehicule Expense'), 'item_group': _('Vehicule Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Travel Expenses'), 'item_name': _('Travel Expenses'), 'item_group': _('Other Travel Related Costs'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Mandatory Personal Social Security Contributions'), 'item_name': _('Mandatory Personal Social Security Contributions'), 'item_group': _('Personal Social Security Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Optional Personal Social Security Contributions'), 'item_name': _('Optional Personal Social Security Contributions'), 'item_group': _('Personal Social Security Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Reception and Representation Expense'), 'item_name': _('Reception and Representation Expense'), 'item_group': _('Reception and Representation Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Consumable Supplies'), 'item_name': _('Consumable Supplies (Stationery, Office Supplies)'), 'item_group': _('Office Supplies, Documentation, Post Office'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Professional Magazine'), 'item_name': _('Professional Magazine'), 'item_group': _('Office Supplies, Documentation, Post Office'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Post Office'), 'item_name': _('Post Office'), 'item_group': _('Office Supplies, Documentation, Post Office'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Deeds and Litigation Expenses'), 'item_name': _('Deeds and Litigation Expenses'), 'item_group': _('Deeds and Litigation Costs'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Certified Management Association'), 'item_name': _('Certified Management Association'), 'item_group': _('Professional Organizations Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('College of Midwifes'), 'item_name': _('College of Midwifes'), 'item_group': _('Professional Organizations Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Midwifes Union'), 'item_name': _('Midwifes Union'), 'item_group': _('Professional Organizations Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Regional Medical Professionals Union'), 'item_name': _('Regional Medical Professionals Union'), 'item_group': _('Professional Organizations Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Bank Account Operating Expenses'), 'item_name': _('Bank Account Operating Expenses'), 'item_group': _('Miscellaneous Management Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Waiting Room Magazines'), 'item_name': _('Waiting Room Magazines'), 'item_group': _('Miscellaneous Management Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Phone Desk Expenses'), 'item_name': _('Phone Desk Expenses'), 'item_group': _('Miscellaneous Management Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Interests and Professional Loan'), 'item_name': _('Interests and Professional Loan'), 'item_group': _('Financial Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
		{'doctype': 'Item', 'item_code': _('Agios'), 'item_name': _('Agios'), 'item_group': _('Financial Expenses'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
	]

	from frappe.modules import scrub
	for r in records:
		print(r)
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError, e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

def codifications(country=None):
	records = [
		#Midwife Codifications
		{'doctype': 'Codification', 'codification': 'C', 'basic_price': 23, 'billing_price': 23, 'codification_name': 'C', 'codification_description': 'Consultation'},
		{'doctype': 'Codification', 'codification': 'V', 'basic_price': 23, 'billing_price': 23, 'codification_name': 'V', 'codification_description': 'Visite'},
		{'doctype': 'Codification', 'codification': 'SF', 'basic_price': 2.80, 'billing_price': 2.80, 'codification_name': 'SF', 'codification_description': 'Actes en SF'},
		{'doctype': 'Codification', 'codification': 'HN', 'basic_price': 0, 'billing_price': 0, 'codification_name': 'HN', 'codification_description': 'Actes Hors Nomenclature'},
		{'doctype': 'Codification', 'codification': 'SF 15', 'basic_price': 42, 'billing_price': 42, 'codification_name': 'SF 15', 'codification_description': 'PNP: Première séance entretien individuel | Sur prescription à domicile: Grossesse unique avec monitoring à partir de 24 sem'},
		{'doctype': 'Codification', 'codification': 'SF 11,6', 'basic_price': 32.48, 'billing_price': 32.48, 'codification_name': 'SF 11,6', 'codification_description': 'PNP: 7 séances suivantes ≤ 3 femmes'},
		{'doctype': 'Codification', 'codification': 'SF 12', 'basic_price': 33.60, 'billing_price': 33.60, 'codification_name': 'SF 12', 'codification_description': 'PNP: 7 séances suivantes individuelles'},
		{'doctype': 'Codification', 'codification': 'SF 16,5', 'basic_price': 46.20, 'billing_price': 46.20, 'codification_name': 'SF 16,5', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J7 (J0 étant le jour de l\'accouchement): Un enfant, les 2 premiers forfaits'},
		{'doctype': 'Codification', 'codification': 'SF 23', 'basic_price': 64.40, 'billing_price': 64.40, 'codification_name': 'SF 23', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J7 (J0 étant le jour de l\'accouchement): Deux enfants et plus, les 2 premiers forfaits'},
		{'doctype': 'Codification', 'codification': 'SF 17', 'basic_price': 47.60, 'billing_price': 47.60, 'codification_name': 'SF 17', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J7 (J0 étant le jour de l\'accouchement): Deux enfants et plus, les forfaits suivants'},
		{'doctype': 'Codification', 'codification': 'SF 7', 'basic_price': 19.60, 'billing_price': 19.60, 'codification_name': 'SF 7', 'codification_description': 'Rééducation périnéo-sphinctérienne'},
		{'doctype': 'Codification', 'codification': 'SF 9', 'basic_price': 25.20, 'billing_price': 25.20, 'codification_name': 'SF 9', 'codification_description': 'Sur prescription à domicile: Surveillance grossesse sans monitoring'},
		{'doctype': 'Codification', 'codification': 'JKLD001', 'basic_price': 38.40, 'billing_price': 38.40, 'codification_name': 'JKLD001', 'codification_description': 'Pose d\'un dispositif intra-utérin'},
		{'doctype': 'Codification', 'codification': 'QZLA004', 'basic_price': 17.99, 'billing_price': 17.99, 'codification_name': 'QZLA004', 'codification_description': 'Pose d\'implant pharmacologique sous-cutané'},
		{'doctype': 'Codification', 'codification': 'QZGA002', 'basic_price': 41.80, 'billing_price': 41.80, 'codification_name': 'QZGA002', 'codification_description': 'Ablation ou changement d\'implant pharmacologique sous-cutané'},
		{'doctype': 'Codification', 'codification': 'JKHD001', 'basic_price': 12.46, 'billing_price': 12.46, 'codification_name': 'JKHD001', 'codification_description': 'Prélèvement cervicovaginal'},
		{'doctype': 'Codification', 'codification': 'SF 6', 'basic_price': 16.80, 'billing_price': 16.80, 'codification_name': 'SF 6', 'codification_description': 'PNP: 7 séances > 3 femmes (max = 6 )'},
		{'doctype': 'Codification', 'codification': 'SF 22', 'basic_price': 61.60, 'billing_price': 61.60, 'codification_name': 'SF 22', 'codification_description': 'Sur prescription à domicile: Grossesse multiple avec monitoring à partir de 24 sem'},
		{'doctype': 'Codification', 'codification': 'SF 19', 'basic_price': 53.20, 'billing_price': 53.20, 'codification_name': 'SF 19', 'codification_description': 'Sur prescription au cabinet: Grossesse multiple avec monitoring à partir de 24 sem'},
		{'doctype': 'Codification', 'codification': 'SP', 'basic_price': 18.55, 'billing_price': 18.55, 'codification_name': 'SP', 'codification_description': 'Séances post-natales (2 séances du 8e jour qui suit l\'accouchement à la CS post-natale)'},
		{'doctype': 'Codification', 'codification': 'SF 22,4', 'basic_price': 62.72, 'billing_price': 62.72, 'codification_name': 'SF 22,4', 'codification_description': 'Ablation DIU par un matériel intra-utérin de préhension par voie vaginale'},
		{'doctype': 'Codification', 'codification': 'JKKD001', 'basic_price': 38.40, 'billing_price': 38.40, 'codification_name': 'JKKD001', 'codification_description': 'Changement d\'un dispositif intra-utérin'},
		{'doctype': 'Codification', 'codification': 'JLLD001', 'basic_price': 0, 'billing_price': 0, 'codification_name': 'JLLD001', 'codification_description': 'Pose de dispositif intra-vaginal'},
		{'doctype': 'Codification', 'codification': 'JLGD001', 'basic_price': 0, 'billing_price': 0, 'codification_name': 'JLGD001', 'codification_description': 'Ablation ou changement de dispositif intra-vaginal'},
		{'doctype': 'Codification', 'codification': 'ZCQM007', 'basic_price': 37.80, 'billing_price': 37.80, 'codification_name': 'ZCQM007', 'codification_description': 'Échographie du petit bassin [pelvis] féminin pour surveillance de l\'ovulation'},
		{'doctype': 'Codification', 'codification': 'ZCQM009', 'basic_price': 42.25, 'billing_price': 42.25, 'codification_name': 'ZCQM009', 'codification_description': 'Échographie-doppler du petit bassin [pelvis] féminin pour surveillance de l\'ovulation'},
		{'doctype': 'Codification', 'codification': 'JNQM001', 'basic_price': 35.65, 'billing_price': 35.65, 'codification_name': 'JNQM001', 'codification_description': 'Échographie non morphologique de la grossesse avant 11 semaines d\'aménorrhée'},
		{'doctype': 'Codification', 'codification': 'JQQM010', 'basic_price': 61.47, 'billing_price': 61.47, 'codification_name': 'JQQM010', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse uniembryonnaire au 1er trimestre'},
		{'doctype': 'Codification', 'codification': 'JQQM015', 'basic_price': 71.57, 'billing_price': 71.57, 'codification_name': 'JQQM015', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse multiembryonnaire au 1er trimestre'},
		{'doctype': 'Codification', 'codification': 'JQQM018', 'basic_price': 100.20, 'billing_price': 100.20, 'codification_name': 'JQQM018', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse unifœtale au 2ème trimestre'},
		{'doctype': 'Codification', 'codification': 'JQQM016', 'basic_price': 100.20, 'billing_price': 100.20, 'codification_name': 'JQQM016', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse unifœtale au 3ème trimestre'},
		{'doctype': 'Codification', 'codification': 'JQQM019', 'basic_price': 154.09, 'billing_price': 154.09, 'codification_name': 'JQQM019', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse multifœtale au 2ème trimestre'},
		{'doctype': 'Codification', 'codification': 'JQQM017', 'basic_price': 154.09, 'billing_price': 154.09, 'codification_name': 'JQQM017', 'codification_description': 'Échographie biométrique et morphologique d\'une grossesse multifœtale au 3ème trimestre'},
		{'doctype': 'Codification', 'codification': 'JQQM002', 'basic_price': 92.19, 'billing_price': 92.19, 'codification_name': 'JQQM002', 'codification_description': 'Échographie d\'une grossesse unifœtale à partir du 2ème trimestre avec échographie-doppler des artères utérines de la mère et des vaisseaux du fœtus, pour souffrance fœtale'},
		{'doctype': 'Codification', 'codification': 'JQQM007', 'basic_price': 133.81, 'billing_price': 133.81, 'codification_name': 'JQQM007', 'codification_description': 'Échographie d\'une grossesse multifœtale à partir du 2ème trimestre avec échographie-doppler des artères utérines de la mère et des vaisseaux des fœtus, pour souffrance fœtale'},
		{'doctype': 'Codification', 'codification': 'JQQM001', 'basic_price': 46.15, 'billing_price': 46.15, 'codification_name': 'JQQM001', 'codification_description': 'Échographie de surveillance de la croissance fœtale'},
		{'doctype': 'Codification', 'codification': 'JQQM003', 'basic_price': 75.60, 'billing_price': 75.60, 'codification_name': 'JQQM003', 'codification_description': 'Échographie de surveillance de la croissance fœtale avec échographie-doppler des artères utérines de la mère et des vaisseaux du fœtus'},
		{'doctype': 'Codification', 'codification': 'IF', 'basic_price': 4, 'billing_price': 4, 'codification_name': 'IF', 'codification_description': 'Indemnité forfaitaire de déplacement', 'lump_sum_travel_allowance': 1},
		{'doctype': 'Codification', 'codification': 'IK', 'basic_price': 0.45, 'billing_price': 0.45, 'codification_name': 'IK_Plaine', 'codification_description': 'Indemnité kilométrique plaine', 'mileage_allowance_lowland': 1},
		{'doctype': 'Codification', 'codification': 'IK', 'basic_price': 0.73, 'billing_price': 0.73, 'codification_name': 'IK_Montagne', 'codification_description': 'Indemnité kilométrique montagne', 'mileage_allowance_mountain': 1},
		{'doctype': 'Codification', 'codification': 'IK', 'basic_price': 3.95, 'billing_price': 3.95, 'codification_name': 'IK_Pied_Ski', 'codification_description': 'Indemnité kilométrique à pied ou à ski', 'mileage_allowance_walking_skiing': 1},
		{'doctype': 'Codification', 'codification': 'P', 'basic_price': 35, 'billing_price': 35, 'codification_name': 'P', 'codification_description': 'Indemnité de nuit de 20h à 0h et de 6h à 8h (appel à partir de 19h)', 'night_work_allowance_1': 1},
		{'doctype': 'Codification', 'codification': 'S', 'basic_price': 40, 'billing_price': 40, 'codification_name': 'S', 'codification_description': 'Indemnité de nuit de 0h à 6h', 'night_work_allowance_2': 1},
		{'doctype': 'Codification', 'codification': 'F', 'basic_price': 21, 'billing_price': 21, 'codification_name': 'F', 'codification_description': 'Indemnité dimanche et jours fériés, en cas d\'urgence dès samedi 12h', 'sundays_holidays_allowance': 1},
		{'doctype': 'Codification', 'codification': 'C + JKHD001', 'basic_price': 35.46, 'billing_price': 35.46, 'codification_name': 'C + JKHD001', 'codification_description': 'Consultation + Prélèvement Cervicovaginal'},
	]

	from frappe.modules import scrub
	for r in records:
		print(r)
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError, e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise
