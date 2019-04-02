# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# License: See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.local.lang = 'fr'
	records = [
		{'doctype': 'Codification', 'codification': 'C + MSF', 'basic_price': 25, 'billing_price': 25, 'codification_name': 'C + MSF', 'codification_description': 'Consultation + Majoration'},
		{'doctype': 'Codification', 'codification': 'V + MSF', 'basic_price': 25, 'billing_price': 25, 'codification_name': 'V + MSF', 'codification_description': 'Visite + Majoration'},
		{'doctype': 'Codification', 'codification': 'SF 12,6', 'basic_price': 35.28, 'billing_price': 35.28, 'codification_name': 'SF 12,6', 'codification_description': 'Bilan prénatal valorisant la prévention et le parcours de soins (1 séance)'},
		{'doctype': 'Codification', 'codification': 'SF 15,6', 'basic_price': 43.68, 'billing_price': 43.68, 'codification_name': 'SF 15,6', 'codification_description': 'Surveillance de grossesse pathologique simple + RCF à partir de 24SA'},
		{'doctype': 'Codification', 'codification': 'SF 22,6', 'basic_price': 63.28, 'billing_price': 63.28, 'codification_name': 'SF 22,6', 'codification_description': 'Surveillance de grossesse pathologique multiple + RCF à partir de 24SA'},
		{'doctype': 'Codification', 'codification': 'SF 12,5', 'basic_price': 35, 'billing_price': 35, 'codification_name': 'SF 12,5', 'codification_description': 'Examen de grossesse simple à partir de la 24ème SA comportant RCF+CR'},
		{'doctype': 'Codification', 'codification': 'SF 19,5', 'basic_price': 54.6, 'billing_price': 54.6, 'codification_name': 'SF 19,5', 'codification_description': 'Examen de grossesse multiple à partir de la 24ème SA comportant RCF+CR'},
		{'doctype': 'Codification', 'codification': 'DSP', 'basic_price': 25, 'billing_price': 25, 'codification_name': 'DSP', 'codification_description': 'Majoration forfaitaire sorties précoces (sur la 1e visite si dans les 24h après la sortie et si à moins de 72h de l’accouchement)'},
		{'doctype': 'Codification', 'codification': 'CCP', 'basic_price': 55.2, 'billing_price': 55.2, 'codification_name': 'CCP', 'codification_description': 'Première consultation de contraception et de prévention des jeunes filles entre 15 et 18 ans'},
		{'doctype': 'Codification', 'codification': 'ZCQJ001', 'basic_price': 69.93, 'billing_price': 69.93, 'codification_name': 'ZCQJ001', 'codification_description': 'Echographie-doppler transcutanée et échographie-doppler par voie rectale et/ou vaginale [par voie cavitaire] du petit bassin [pelvis] féminin'},
		{'doctype': 'Codification', 'codification': 'ZCQJ002', 'basic_price': 69.93, 'billing_price': 69.93, 'codification_name': 'ZCQJ002', 'codification_description': 'Échographie-doppler du petit bassin [pelvis] féminin, par voie rectale et/ou vaginale [par voie cavitaire]'},
		{'doctype': 'Codification', 'codification': 'ZCQJ003', 'basic_price': 52.45, 'billing_price': 52.45, 'codification_name': 'ZCQJ003', 'codification_description': 'Échographie du petit bassin [pelvis] féminin, par voie rectale et/ou vaginale [par voie cavitaire]'},
		{'doctype': 'Codification', 'codification': 'ZCQJ006', 'basic_price': 56.7, 'billing_price': 56.7, 'codification_name': 'ZCQJ006', 'codification_description': 'Echographie transcutanée avec échographie par voie rectale et/ou vaginale [par voie cavitaire] du petit bassin [pelvis] féminin'},
		{'doctype': 'Codification', 'codification': 'ZCQM003', 'basic_price': 52.45, 'billing_price': 52.45, 'codification_name': 'ZCQM003', 'codification_description': 'Échographie transcutanée du petit bassin [pelvis] féminin'}
	]

	for r in records:
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise

	records= [
		{'doctype': 'Codification', 'codification': 'SF 16,5', 'basic_price': 46.20, 'billing_price': 46.20, 'codification_name': 'SF 16,5', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J12 (J0 étant le jour de l\'accouchement): Un enfant, les 2 premiers forfaits'},
		{'doctype': 'Codification', 'codification': 'SF 23', 'basic_price': 64.40, 'billing_price': 64.40, 'codification_name': 'SF 23', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J12 (J0 étant le jour de l\'accouchement): Deux enfants et plus, les 2 premiers forfaits'},
		{'doctype': 'Codification', 'codification': 'SF 17', 'basic_price': 47.60, 'billing_price': 47.60, 'codification_name': 'SF 17', 'codification_description': 'Forfait journalier de SURVEILLANCE MERE-ENFANT à domicile de J1 à J12 (J0 étant le jour de l\'accouchement): Deux enfants et plus, les forfaits suivants'}
	]

	for r in records:
		frappe.db.set_value(r.get("doctype"), r.get("codification"), "codification_description", r.get("codification_description"))
