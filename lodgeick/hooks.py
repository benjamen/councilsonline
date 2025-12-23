app_name = "lodgeick"
app_title = "Lodgeick"
app_publisher = "Optified"
app_description = "Lodgeick"
app_email = "contact@optified.nz"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "lodgeick",
# 		"logo": "/assets/lodgeick/logo.png",
# 		"title": "Lodgeick",
# 		"route": "/lodgeick",
# 		"has_permission": "lodgeick.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/lodgeick/css/request_status.css"
]

app_include_js = [
	"/assets/lodgeick/js/action_bar_utils.js",
	"/assets/lodgeick/js/summary_dashboard.js",
	"/assets/lodgeick/js/status_pill.js",
	"/assets/lodgeick/js/workflow_progression.js",
	"/assets/lodgeick/js/timeline_visual.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/lodgeick/css/lodgeick.css"
# web_include_js = "/assets/lodgeick/js/lodgeick.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lodgeick/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "lodgeick/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "frontend"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website Route Rules
# -------------------
# Route all /frontend/* paths to the frontend.py handler for SPA routing
# Route /council/* to council_landing_page handler for public council pages
website_route_rules = [
	{"from_route": "/frontend/<path:app_path>", "to_route": "frontend"},
	{"from_route": "/council/<council_code>", "to_route": "council_landing_page"},
]

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "lodgeick.utils.jinja_methods",
# 	"filters": "lodgeick.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "lodgeick.install.before_install"
after_install = "lodgeick.install.after_install"

# Fixtures
# --------
# Load fixtures from JSON files on migrate/install
fixtures = [
	{"dt": "Print Format", "filters": [["module", "=", "Lodgeick"]]},
	{"dt": "Workspace", "filters": [["module", "=", "Lodgeick"]]},
	{"dt": "Number Card", "filters": [["module", "=", "Lodgeick"]]},
	{"dt": "Dashboard Chart", "filters": [["module", "=", "Lodgeick"]]},
	"lodgeick.lodgeick.lodgeick.fixtures.request_types",
	# REMOVED: Multi-instance councils fixture (now using Single DocType)
	# "lodgeick.lodgeick.lodgeick.fixtures.councils",
	"lodgeick.lodgeick.lodgeick.fixtures.taytay.taytay_council",  # Single DocType Council
	"lodgeick.lodgeick.lodgeick.fixtures.council_request_types",
	"lodgeick.lodgeick.lodgeick.fixtures.assessment_stage_types",
	"lodgeick.lodgeick.lodgeick.fixtures.assessment_templates",
	"lodgeick.lodgeick.lodgeick.fixtures.task_templates_spisc"
]

# Uninstallation
# ------------

# before_uninstall = "lodgeick.uninstall.before_uninstall"
# after_uninstall = "lodgeick.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "lodgeick.utils.before_app_install"
# after_app_install = "lodgeick.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "lodgeick.utils.before_app_uninstall"
# after_app_uninstall = "lodgeick.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lodgeick.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# Project Task handles all validation and costing in its own class methods
	# No external hooks needed
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"lodgeick.tasks.rfi_reminders.send_rfi_due_date_reminders",
		"lodgeick.tasks.rfi_reminders.escalate_overdue_rfis"
	]
}

# Testing
# -------

# before_tests = "lodgeick.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "lodgeick.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lodgeick.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lodgeick.utils.before_request"]
after_request = ["lodgeick.utils.after_request"]

# Job Events
# ----------
# before_job = ["lodgeick.utils.before_job"]
# after_job = ["lodgeick.utils.after_job"]

# Custom Commands
# ---------------
# Add custom bench commands
commands = [
	"lodgeick.lodgeick.commands.install_default_data"
]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lodgeick.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

