# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version
from frappe import _

app_name = "maia"
app_title = "Maia"
app_publisher = "DOKOS"
app_description = "Patient Record Management App for Midwifes"
app_icon = "octicon octicon-squirrel"
app_color = "#ff4081"
app_email = "hello@dokos.io"
app_license = "AGPLv3"


fixtures = ["Custom Field", {"doctype": "Role", "filters": {"name": "Midwife"}}]

error_report_email = "hello@dokos.io"

app_include_js = "assets/js/maia.min.js"
app_include_css = "assets/css/maia.min.css"

doctype_js = {
	"Google Calendar": "public/js/maia/google_calendar.js",
	"Google Settings": "public/js/maia/google_settings.js",
	"Address": "public/js/maia/address.js"
}


website_context = {
	"favicon": "/assets/maia/favicon.png",
	"splash_image": "/assets/maia/images/maia_squirrel.svg"
}

# Migration
#----------
before_migrate = [
	"maia.customizations.before_migration_hooks.before_migrate"
]

# after install
after_install = "maia.setup.setup_wizard.setup_wizard.setup_complete"

domains = {
	'Sage-Femme': 'maia.domains.midwife'
}

jinja_template_functions = "maia.utilities.utils.custom_template_functions"
boot_session = "maia.startup.boot.boot_session"

# welcome message title
login_mail_title = "Nous sommes heureux de vous compter parmi nous !"

# calendar
calendars = ["Maia Appointment"]

gcalendar_integrations = {
	"Maia Appointment": {
		"pull_insert": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.insert_event_to_calendar",
		"pull_update": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.update_event_in_calendar",
		"pull_delete": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.cancel_event_in_calendar"
	}
}


# default footer
default_mail_footer = """<div style="text-align: center;">
	<a href="https://maia-by-dokos.fr" target="_blank" style="color: #8d99a6;">
		Envoyé par MAIA
	</a>
</div>"""

website_route_rules = [
	{"from_route": "/my-appointments", "to_route": "Maia Appointment"},
	{"from_route": "/my-appointments/<path:name>", "to_route": "appointment_details",
		"defaults": {
			"doctype": "Maia Appointment",
			"parents": [{"label": "Mes Rendez-Vous", "route": "my-appointments"}]
		}
	},
	{"from_route": "/receipts", "to_route": "Revenue"},
	{"from_route": "/receipts/<path:name>", "to_route": "receipt",
		"defaults": {
			"doctype": "Revenue",
			"parents": [{"label": _("Receipts"), "route": "receipts"}]
		}
	},
]

standard_portal_menu_items = [
	{"title": _("Prendre rendez-Vous"), "route": "/appointment",
		"reference_doctype": "Maia Appointment", "role": "Patient"},
	{"title": _("Mes rendez-Vous"), "route": "/my-appointments",
		"reference_doctype": "Maia Appointment", "role": "Patient"},
	{"title": _("Mes reçus"), "route": "/receipts",
		"reference_doctype": "Revenue", "role": "Patient"}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/maia/css/maia.css"
# app_include_js = "/assets/maia/js/maia.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/maia/css/maia.css"
# web_include_js = "/assets/maia/js/maia.js"

# Home Pages
# ----------

# application home page (will override Website Settings)

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "maia.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "maia.install.before_install"
# after_install = "maia.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config
notification_config = "maia.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
permission_query_conditions = {
	"Revenue": "maia.maia_accounting.doctype.revenue.revenue.get_permission_query_conditions",
	"Expense": "maia.maia_accounting.doctype.expense.expense.get_permission_query_conditions",
	"Miscellaneous Operation": "maia.maia_accounting.doctype.miscellaneous_operation.miscellaneous_operation.get_permission_query_conditions",
	"Payment": "maia.maia_accounting.doctype.payment.payment.get_permission_query_conditions",
	"General Ledger Entry": "maia.maia_accounting.doctype.general_ledger_entry.general_ledger_entry.get_permission_query_conditions"
}

has_permission = {
	"Revenue": "maia.maia_accounting.utils.has_accounting_permissions",
	"Expense": "maia.maia_accounting.utils.has_accounting_permissions",
	"Miscellaneous Operation": "maia.maia_accounting.utils.has_accounting_permissions",
	"Payment": "maia.maia_accounting.utils.has_accounting_permissions",
	"General Ledger Entry": "maia.maia_accounting.utils.has_accounting_permissions"
}

has_website_permission = {
	"Revenue": "maia.controllers.website_list_for_contact.has_website_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Website Settings": {
		"on_update": "maia.customizations.doc_events.check_default_web_role"
	},
	"Maia Appointment": {
		"after_insert": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.insert_event_in_google_calendar",
		"on_update": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.update_event_in_google_calendar",
		"on_cancel": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.delete_event_in_google_calendar",
		"on_trash": "maia.maia_appointment.doctype.maia_appointment.maia_appointment.delete_event_in_google_calendar"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# 	"all": [
	# 		"maia.tasks.all"
	# 	],
	"daily": [
		"maia.maia_accounting.doctype.maia_asset.maia_asset.post_depreciations",
		"maia.tasks.update_patient_birthday",
		"maia.maia_accounting.utils.auto_create_fiscal_year"
	],
	"hourly": [
		"maia.maia_appointment.doctype.maia_appointment.maia_appointment.flush"
	]
	# 	"weekly": [
	# 		"maia.tasks.weekly"
	# 	]
	# 	"monthly": [
	# 		"maia.tasks.monthly"
	# 	]
}

# Testing
# -------

# before_tests = "maia.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "maia.event.get_events"
# }

auto_cancel_exempted_doctypes = ["Revenue", "General Ledger Entry", "Payment"]