from __future__ import unicode_literals
from frappe import _
import frappe
import datetime as dt

def get_data():

	return [
		{
			"label": _("Patients"),
			"icon": "icon-star",
			"items": [
					{
						"type": "doctype",
						"name": "Patient Record",
						"label": _("Patient Record"),
						"description": _("Patient Record"),
						"onboard": 1
					},
					{
						"type": "doctype",
						"name": "Free Prescription",
						"label": _("Free Prescriptions"),
						"description": _("Free Prescriptions"),
						"onboard": 1
					},
					{
						"type": "doctype",
						"name": "Address",
						"label": _("Addresses"),
						"description": _("Addresses"),
					}
				]
			},
		{
			"label": _("Folders"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Pregnancy",
					"label": _("Pregnancy"),
					"description": _("Pregnancy"),

				},
				{
					"type": "doctype",
					"name": "Prenatal Interview",
					"label": _("Prenatal Interview"),
					"description": _("Prenatal Interview"),

				},
				{

					"type": "doctype",
					"name": "Perineum Rehabilitation",
					"label": _("Perineum Rehabilitation"),
					"description": _("Perineum Rehabilitation"),

				},
				{
					"type": "doctype",
					"name": "Gynecology",
					"label": _("Gynecology"),
					"description": _("Gynecology"),

				},
			]
		},
		{
			"label": _("Consultations"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Pregnancy Consultation",
					"label": _("Pregnancy Consultation"),
					"description": _("Pregnancy Consultation"),
				},
				{
					"type": "doctype",
					"name": "Birth Preparation Consultation",
					"label": _("Birth Preparation Consultation"),
					"description": _("Birth Preparation Consultation"),
				},
				{
					"type": "doctype",
					"name": "Early Postnatal Consultation",
					"label": _("Early Postnatal Consultation"),
					"description": _("Early Postnatal Consultation"),
				},
				{
					"type": "doctype",
					"name": "Postnatal Consultation",
					"label": _("Postnatal Consultation"),
					"description": _("Postnatal Consultation"),
				},
				{
					"type": "doctype",
					"name": "Perineum Rehabilitation Consultation",
					"label": _("Perineum Rehabilitation Consultation"),
					"description": _("Perineum Rehabilitation Consultation"),
				},
				{
					"type": "doctype",
					"name": "Gynecological Consultation",
					"label": _("Gynecological Consultation"),
					"description": _("Gynecological Consultation"),
				},
				{
					"type": "doctype",
					"name": "Free Consultation",
					"label": _("Free Consultation"),
					"description": _("Free Consultation"),
				},

				]
		},
		{
			"label": _("Setup"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Professional Information Card",
					"label": _("Professional Information Card"),
					"description": _("Professional Information Card"),
				},
				{
					"type": "doctype",
					"name": "Codification",
					"label": _("Codifications"),
					"description": _("Codifications"),
				},
				{
					"type": "doctype",
					"name": "Lab Exam Type",
					"label": _("Lab Exam Types"),
					"description": _("Lab Exam Types"),
				},
				{
					"type": "doctype",
					"name": "Lab Exam Template",
					"label": _("Lab Exam Templates"),
					"description": _("Lab Exam Template"),
				},
				{
					"type": "doctype",
					"name": "Drug List Template",
					"label": _("Drug List Templates"),
					"description": _("Drug List Template"),
				},
				{
					"type": "doctype",
					"name": "Maternity",
					"label": _("Maternities"),
					"description": _("Maternity"),
				},
				{
					"type": "doctype",
					"name": "Origin",
					"label": _("Origins"),
					"description": _("Origin"),
				},
				{
					"type": "doctype",
					"name": "Profession",
					"label": _("Professions"),
					"description": _("Professions"),
				},
				{
					"type": "doctype",
					"name": "Employment Status",
					"label": _("Employment Statuses"),
					"description": _("Employment Statuses"),
				},
				{
					"type": "doctype",
					"name": "Sport",
					"label": _("Sports"),
					"description": _("Sports"),
				}
			]
		},
		{
			"label": _("Medical Master Data"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Addiction",
					"label": _("Addictions"),
					"description": _("Addiction"),
				},
				{
					"type": "doctype",
					"name": "Allergia",
					"label": _("Allergia"),
					"description": _("Allergia"),
				},
				{
					"type": "doctype",
					"name": "Anesthesia Type",
					"label": _("Anesthesia Types"),
					"description": _("Anesthesia Type"),
				},
				{
					"type": "doctype",
					"name": "Contraception",
					"label": _("Contraceptions"),
					"description": _("Contraception"),
				},
				{
					"type": "doctype",
					"name": "Delivery Way",
					"label": _("Delivery Ways"),
					"description": _("Delivery Way"),
				},
				{
					"type": "doctype",
					"name": "Vaccine",
					"label": _("Vaccines"),
					"description": _("Vaccines"),
				}
			]
		},
		{
			"label": _("Replacements"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Replacement",
					"label": _("Replacement"),
					"description": _("Replacement"),
				},
				{
					"type": "report",
					"name": "Midwife Replacement Report",
					"label": _("Replacement Report"),
					"is_query_report": True,
				}
			]
		}

	]
