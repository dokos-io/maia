# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
	initial_list = ['Stock', 'Manufacturing', 'Learn', 'Buying', 'Selling', 'Support', 'Integrations', 'Maintenance', 'Schools', 'HR', 'CRM', 'Employee', 'Issue',
					'Lead', 'POS', 'Student', 'Student Group', 'Course Schedule', 'Student Attendance', 'Course', 'Program', 'Student Applicant', 'Fees', 'Instructor', 'Room', 'Leaderboard',
					'Student Attendance Tool', 'Education', 'Healthcare', 'Hub', 'Data Import', 'Restaurant', 'Agriculture', 'Crop', 'Crop Cycle', 'Fertilizer', 'Land Unit', 'Disease', 'Plant Analysis',
					'Soil Analysis', 'Soil Texture', 'Water Analysis', 'Weather', 'Grant Application', 'Donor', 'Volunteer', 'Member', 'Chapter', 'Non Profit']
	hidden_list = []

	for i in initial_list:
		try:
			frappe.get_doc('Desktop Icon', {'standard': 1, 'label': i})
			frappe.db.set_value("Desktop Icon", dict(module_name="i"), "blocked", 1)
		except Exception as e:
			print(e)

	frappe.db.commit()
