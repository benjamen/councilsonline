app_name = "councilsonline"
app_title = "CouncilsOnline"
app_publisher = "Optified"
app_description = "CouncilsOnline"
app_email = "contact@optified.nz"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "councilsonline",
# 		"logo": "/assets/councilsonline/logo.png",
# 		"title": "CouncilsOnline",
# 		"route": "/councilsonline",
# 		"has_permission": "councilsonline.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/councilsonline/css/request_status.css"
]

app_include_js = [
	"/assets/councilsonline/js/action_bar_utils.js",
	"/assets/councilsonline/js/summary_dashboard.js",
	"/assets/councilsonline/js/status_pill.js",
	"/assets/councilsonline/js/workflow_progression.js",
	"/assets/councilsonline/js/timeline_visual.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/councilsonline/css/councilsonline.css"
# web_include_js = "/assets/councilsonline/js/councilsonline.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "councilsonline/public/scss/website"

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
# app_include_icons = "councilsonline/public/icons.svg"

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
# 	"methods": "councilsonline.utils.jinja_methods",
# 	"filters": "councilsonline.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "councilsonline.install.before_install"
after_install = "councilsonline.install.after_install"

# Setup Wizard
# ------------
# Add configuration pack selection to setup wizard
setup_wizard_requires = "councilsonline/public/js/setup_wizard.js"
setup_wizard_stages = "councilsonline.setup.setup_wizard.get_setup_stages"
setup_wizard_complete = "councilsonline.setup.setup_wizard.on_setup_complete"

# Fixtures
# --------
# Load BASE fixtures on migrate/install (region-specific loaded via config packs)
fixtures = [
	# Core Frappe fixtures
	{"dt": "Print Format", "filters": [["module", "=", "CouncilsOnline"]]},
	{"dt": "Workspace", "filters": [["module", "=", "CouncilsOnline"]]},
	{"dt": "Number Card", "filters": [["module", "=", "CouncilsOnline"]]},
	{"dt": "Dashboard Chart", "filters": [["module", "=", "CouncilsOnline"]]},
	# Base roles (always needed)
	{"dt": "Role", "filters": [["name", "in", [
		"CouncilsOnline Admin", "CouncilsOnline Manager", "CouncilsOnline User",
		"Council Admin", "Council Manager", "Council Staff", "Council Planner",
		"Applicant", "Requester", "Agent"
	]]]},
	# Base workflow (always needed)
	{"dt": "Workflow", "filters": [["document_type", "in", ["Request", "SPISC Application", "Resource Consent Application"]]]},
	# Assessment stage types (base infrastructure)
	"councilsonline.councilsonline.councilsonline.fixtures.assessment_stage_types",
	# NOTE: Region-specific fixtures (request_types, assessment_templates, council configs)
	# are now installed via configuration packs using:
	#   bench --site <site> install-config-packs --pack nz_resource_consent
	#   bench --site <site> install-config-packs --pack ph_social_services
]

# Uninstallation
# ------------

# before_uninstall = "councilsonline.uninstall.before_uninstall"
# after_uninstall = "councilsonline.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "councilsonline.utils.before_app_install"
# after_app_install = "councilsonline.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "councilsonline.utils.before_app_uninstall"
# after_app_uninstall = "councilsonline.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "councilsonline.notifications.get_notification_config"

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
		"councilsonline.tasks.rfi_reminders.send_rfi_due_date_reminders",
		"councilsonline.tasks.rfi_reminders.escalate_overdue_rfis"
	]
}

# Testing
# -------

# before_tests = "councilsonline.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "councilsonline.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "councilsonline.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["councilsonline.utils.before_request"]
# after_request = ["councilsonline.utils.after_request"]  # Disabled - function doesn't exist

# Job Events
# ----------
# before_job = ["councilsonline.utils.before_job"]
# after_job = ["councilsonline.utils.after_job"]

# Custom Commands
# ---------------
# Add custom bench commands for configuration pack management
commands = [
	"councilsonline.commands"  # Includes install-config-packs, list-config-packs, show-config-pack
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
# 	"councilsonline.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

