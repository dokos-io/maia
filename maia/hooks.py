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
app_license = "GNU-GPLv3.0"


fixtures = ["Custom Field", {"doctype": "Role", "filters": {"name": "Midwife"}}, {
	"doctype": "Print Format", "filters": {"name": "Facture Maia"}}]

error_report_email = "hello@dokos.io"

app_include_js = "assets/js/maia.min.js"
app_include_css = "assets/maia/css/maia.css"

website_context = {
	"favicon": "/assets/maia/favicon.png",
	"splash_image": "/assets/maia/images/maia_squirrel.svg"
}

# Migration
#----------
before_migrate = ["maia.customizations.demo.add_demo_page",
	"maia.customizations.before_migration_hooks.before_migrate"
]

# after install
after_install = "maia.setup.setup_wizard.setup_wizard.setup_complete"

domains = {
	'Sage-Femme': 'maia.domains.midwife'
}

jinja_template_functions = "maia.utilities.utils.custom_template_functions"

# welcome message title
login_mail_title = "Nous sommes heureux de vous compter parmi nous !"

# calendar
calendars = ["Maia Appointment"]

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
	 }
]

standard_portal_menu_items = [
	{"title": _("Prendre Rendez-Vous"), "route": "/appointment",
	 "reference_doctype": "Maia Appointment", "role": "Customer"},
	{"title": _("Mes Rendez-Vous"), "route": "/my-appointments",
	 "reference_doctype": "Maia Appointment", "role": "Customer"}
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

# notification_config = "maia.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Website Settings": {
		"on_update": "maia.customizations.doc_events.check_default_web_role"
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
		"maia.tasks.update_patient_birthday"
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
