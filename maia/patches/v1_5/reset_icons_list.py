# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.desk.doctype.desktop_icon.desktop_icon import set_hidden_list


def execute():
	initial_list = ['Stock', 'Manufacturing', 'Learn', 'Buying', 'Selling', 'Support', 'Integrations', 'Maintenance', 'Schools', 'HR', 'CRM', 'Employee', 'Issue',
					'Lead', 'POS', 'Student', 'Student Group', 'Course Schedule', 'Student Attendance', 'Course', 'Program', 'Student Applicant', 'Fees', 'Instructor', 'Room', 'Leaderboard',
					'Student Attendance Tool', 'Education', 'Healthcare', 'Hub', 'Data Import', 'Restaurant', 'Agriculture', 'Crop', 'Crop Cycle', 'Fertilizer', 'Land Unit', 'Disease', 'Plant Analysis',
					'Soil Analysis', 'Soil Texture', 'Water Analysis', 'Weather', 'Grant Application', 'Donor', 'Volunteer', 'Member', 'Chapter', 'Non Profit']
	hidden_list = []

	for i in initial_list:
		try:
			frappe.get_doc('Desktop Icon', {'standard': 1, 'module_name': i})
			hidden_list.append(i)
		except Exception:
			pass

	set_hidden_list(hidden_list)
