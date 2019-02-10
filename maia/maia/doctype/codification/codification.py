# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class Codification(Document):
	def on_update(self):
		#Item and Price List update --> if (change_in_item)
		if(self.change_in_item and self.item):
			updating_item(self)
			updating_billing_price(self)
			frappe.db.set_value(self.doctype,self.name,"change_in_item",0)
		elif(self.item):
			frappe.db.set_value("Item",self.item,"disabled",0)
		self.reload()

	def after_insert(self):
		create_item_from_codification(self)

	#Call before delete the codification
	def on_trash(self):
		# remove codification reference from item and disable item
		if(self.item):
			try:
				frappe.delete_doc("Item",self.item)
			except Exception, e:
				frappe.throw(__("""Please Disable the Codification"""))


def updating_item(self):
	frappe.db.sql("""update `tabItem` set item_name=%s, item_group=%s, disabled=0,
			description=%s, modified=NOW() where item_code=%s""",
		      (self.codification, "Codifications" , self.codification_description, self.item))

def updating_billing_price(self):
	frappe.db.sql("""update `tabItem Price` set item_name=%s, price_list_rate=%s, modified=NOW() where item_code=%s and price_list=%s""",(self.codification, self.billing_price, self.item, 'Sage Femme'))
	
	frappe.db.sql("""update `tabItem Price` set item_name=%s, price_list_rate=%s, modified=NOW() where item_code=%s and price_list=%s""",(self.codification, self.basic_price, self.item, 'Securite Sociale'))


def create_item_from_codification(doc):
	disabled = 0

	if frappe.db.get_value("Item Group", {"item_group_name": "Codifications"}) is None:
		create_item_group()
	
	#insert item
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": doc.codification_name,
		"item_name":doc.codification,
		"item_group": "Codifications",
		"description":doc.codification_description,
		"is_sales_item": 1,
		"is_service_item": 1,
		"is_purchase_item": 0,
		"is_stock_item": 0,
		"show_in_website": 0,
		"is_pro_applicable": 0,
		"disabled": disabled,
		"stock_uom": _('Unit')
	}).insert(ignore_permissions=True)

	#insert item price
	#get item price list to insert item price
	if(doc.billing_price != 0.0):
		if (frappe.db.get_value("Price List", {"name": "Sage Femme"})):
			price_list_name = frappe.db.get_value("Price List", {"name": "Sage Femme"})
		else:
			create_price_list("Sage Femme")
			price_list_name = frappe.db.get_value("Price List", {"name": "Sage Femme"})
			
		if(doc.billing_price):
			make_item_price(item.name, price_list_name, doc.billing_price)
		else:
			make_item_price(item.name, price_list_name, 0.0)
			
	if(doc.basic_price != 0.0):
		if (frappe.db.get_value("Price List", {"name": "CPAM"})):
			price_list_name = frappe.db.get_value("Price List", {"name": "CPAM"})
		else:
			create_price_list("CPAM")
			price_list_name = frappe.db.get_value("Price List", {"name": "CPAM"})
			
		if(doc.basic_price):
			make_item_price(item.name, price_list_name, doc.basic_price)
		else:
			make_item_price(item.name, price_list_name, 0.0)
	
	frappe.db.set_value("Codification", doc.name, "item", item.name)

	doc.reload() #refresh the doc after insert.

def make_item_price(item, price_list_name, item_price):
	frappe.get_doc({
		"doctype": "Item Price",
		"price_list": price_list_name,
		"item_code": item,
		"price_list_rate": item_price
	}).insert(ignore_permissions=True)

def create_price_list(price_list_name):
	frappe.get_doc({
		"doctype": "Price List",
		"price_list_name": price_list_name,
		"currency": "EUR",
		"selling": 1
	}).insert(ignore_permissions=True)

def create_item_group():
	frappe.get_doc({
		"doctype": "Item Group",
		"item_group_name": "Codifications",
		"parent_item_group": "All Item Groups"
	}).insert(ignore_permissions=True)
	
@frappe.whitelist()
def change_codification(codification, doc):
	args = json.loads(doc)
	doc = frappe._dict(args)

	item_exist = frappe.db.exists({
		"doctype": "Item",
		"item_code": codification})
	if(item_exist):
		frappe.throw("Code '"+codification+"' already exist !")
	else:
		frappe.rename_doc("Item", doc.name, codification, ignore_permissions = True)
		frappe.db.set_value("Codification",doc.name,"codification",codification)
		frappe.rename_doc("Codification", doc.name, codification, ignore_permissions = True)
	return codification

@frappe.whitelist()
def disable_enable_codification(status, name):
	frappe.db.set_value("Codification",name,"disabled",status)
