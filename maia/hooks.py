# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "maia"
app_title = "Maia"
app_publisher = "DOKOS"
app_description = "Patient Record Management App for Midwifes"
app_icon = "octicon octicon-squirrel"
app_color = "#ff4081"
app_email = "hello@dokos.io"
app_license = "MIT"


fixtures = ["Custom Field", {"doctype": "Role", "filters": {"name": "Midwife"}}]

error_report_email = "hello@dokos.io"

app_include_js = "assets/js/maia.min.js"

website_context = {
    "favicon": "/assets/maia/favicon.png",
    "splash_image": "/assets/maia/images/maia_squirrel.svg"
    }

# setup wizard
setup_wizard_requires = "assets/maia/js/setup_wizard.js"
setup_wizard_complete = "maia.setup.setup_wizard.setup_wizard.setup_complete"

get_help_messages = "maia.utilities.activation.get_help_messages"

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
# home_page = "login"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"maia.tasks.all"
# 	],
# 	"daily": [
# 		"maia.tasks.daily"
# 	],
# 	"hourly": [
# 		"maia.tasks.hourly"
# 	],
# 	"weekly": [
# 		"maia.tasks.weekly"
# 	]
# 	"monthly": [
# 		"maia.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "maia.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "maia.event.get_events"
# }

