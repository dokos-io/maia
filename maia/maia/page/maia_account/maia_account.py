# Copyright (c) 2019, DOKOS and Contributors

import frappe
import requests
from requests.exceptions import HTTPError
import json

BASE_URL = "https://dashboard.dokos.io"

class DokosApiRequest():
	def __init__(self, url):
		self.api_key = frappe.conf.get("dokos_key")
		self.api_secret = frappe.conf.get("dokos_secret")
		self.url = url

		self.setup_headers()

	def setup_headers(self):
		try:
			self.headers = {
				'Authorization': "token {0}:{1}".format(self.api_key, self.api_secret)
			}
		except Exception as e:
			frappe.log_error(e, "Dokos API Error")

	def get_request(self, data):
		return self.make_request("GET", data)

	def post_request(self, data):
		return self.make_request("POST", data)

	def put_request(self, data):
		return self.make_request("PUT", data)

	def make_request(self, method, data=None):
		try:
			data_param = {"data": data} if data else {}
			response = requests.request(method, self.url, headers=self.headers, data=data_param)
			response.raise_for_status()
		except HTTPError as http_err:
			frappe.log_error(http_err, "Dokos API Error")
		except Exception as err:
			frappe.log_error(frappe.get_traceback(), "Dokos API Error")
		else:
			return response.json()

@frappe.whitelist()
def get_invoices(options):
	if frappe.conf.get("dokos_customer"):
		data = {'customer': frappe.conf.get("dokos_customer"), 'options': options}
		request = DokosApiRequest("{0}/api/method/dokops.api.get_account_invoices".format(BASE_URL))
		response = request.post_request(json.dumps(data))
		return response

@frappe.whitelist()
def get_account_details():
	if frappe.conf.get("dokos_customer"):
		data = {"customer": frappe.conf.get("dokos_customer")}
		request = DokosApiRequest("{0}/api/method/dokops.api.get_customer_account_details".format(BASE_URL))
		response = request.post_request(json.dumps(data))
		return response

@frappe.whitelist()
def update_address(data, name):
	request = DokosApiRequest("{0}/api/resource/Address/{1}".format(BASE_URL, name))
	return request.put_request(data)

@frappe.whitelist()
def add_address(data, customer):
	data = json.loads(data)
	data["is_primary_address"] = 1
	data["links"] = [{
		"link_doctype": "Customer",
		"link_name": customer,
		"link_title": customer
	}]
	data["address_type"] = "Billing"
	data["address_title"] = "{0}".format(customer)

	request = DokosApiRequest("{0}/api/resource/Address".format(BASE_URL))
	return request.post_request(data)

@frappe.whitelist()
def get_customer_payment_methods():
	if frappe.conf.get("dokos_customer"):
		data = {"customer": frappe.conf.get("dokos_customer")}
		request = DokosApiRequest("{0}/api/method/dokops.api.get_customer_payment_methods".format(BASE_URL))
		return request.post_request(json.dumps(data))

@frappe.whitelist()
def remove_card(card):
	if frappe.conf.get("dokos_customer"):
		data = {"card": card, "customer": frappe.conf.get("dokos_customer")}
		request = DokosApiRequest("{0}/api/method/dokops.api.remove_payment_card".format(BASE_URL))
		return request.post_request(json.dumps(data))

@frappe.whitelist()
def get_stripe_public_key():
	if frappe.conf.get("dokos_customer"):
		data = {"customer": frappe.conf.get("dokos_customer")}
		request = DokosApiRequest("{0}/api/method/dokops.api.get_stripe_publishable_key".format(BASE_URL))
		return request.post_request(json.dumps(data))

@frappe.whitelist()
def create_new_card(token):
	if token and frappe.conf.get("dokos_customer"):
		token = json.loads(token)
		data = {"card": token.get("token", {}).get("id"), "customer": frappe.conf.get("dokos_customer")}
		request = DokosApiRequest("{0}/api/method/dokops.api.add_new_payment_card".format(BASE_URL))
		return request.post_request(json.dumps(data))

@frappe.whitelist()
def validate_account():
	return True if frappe.conf.get("dokos_customer") else False
