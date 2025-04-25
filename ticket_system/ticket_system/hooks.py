app_name = "ticket_system"
app_title = "نظام حجز التذاكر"
app_publisher = "المنتصر للنقل الدولي"
app_description = "نظام متكامل لحجز التذاكر وإدارة المسارات والوكلاء"
app_email = "support@example.com"
app_license = "MIT"
app_icon = "octicon octicon-file-directory"
app_color = "blue"
app_version = "0.0.1"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/ticket_system/css/ticket_system.css"
app_include_js = "/assets/ticket_system/js/ticket_system.js"

# include js, css files in header of web template
web_include_css = "/assets/ticket_system/css/ticket_system_web.css"
web_include_js = "/assets/ticket_system/js/ticket_system_web.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "login"

# website user home page (by Role)
role_home_page = {
    "Administrator": "ticket-system-dashboard",
    "System Manager": "ticket-system-dashboard",
    "Ticket Manager": "ticket-system-dashboard",
    "Agent": "agent-dashboard",
    "Booking Staff": "booking-dashboard"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = []

# Fixtures
# --------
fixtures = [
    "Role",
    "Role Profile",
    "Custom Field",
    "Property Setter",
    "Print Format",
    "Workflow",
    "Workflow State",
    "Workflow Action"
]

# Installation
# ------------

before_install = "ticket_system.setup.before_install"
after_install = "ticket_system.setup.after_install"

# Uninstallation
# ------------

before_uninstall = "ticket_system.setup.before_uninstall"
after_uninstall = "ticket_system.setup.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps

# override_doctype_class = {
#     "ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Ticket": {
        "after_insert": "ticket_system.controllers.ticket_controller.after_ticket_insert",
        "on_update": "ticket_system.controllers.ticket_controller.on_ticket_update",
        "on_cancel": "ticket_system.controllers.ticket_controller.on_ticket_cancel",
    },
    "Agent Request": {
        "after_insert": "ticket_system.controllers.agent_request_controller.after_request_insert",
        "on_update": "ticket_system.controllers.agent_request_controller.on_request_update",
        "on_submit": "ticket_system.controllers.agent_request_controller.on_request_submit",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "ticket_system.tasks.daily"
    ],
    "hourly": [
        "ticket_system.tasks.hourly"
    ],
    "weekly": [
        "ticket_system.tasks.weekly"
    ],
    "monthly": [
        "ticket_system.tasks.monthly"
    ]
}

# Testing
# -------

# before_tests = "ticket_system.install.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "ticket_system.event.get_events"
# }

# Each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#     "Task": "ticket_system.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Request Events
# --------------
# before_request = ["ticket_system.utils.before_request"]
# after_request = ["ticket_system.utils.after_request"]

# Job Events
# ----------
# before_job = ["ticket_system.utils.before_job"]
# after_job = ["ticket_system.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filter_by": "{filter_by}",
#         "redact_fields": ["{field_1}", "{field_2}"],
#         "partial": 1,
#     },
#     {
#         "doctype": "{doctype_2}",
#         "filter_by": "{filter_by}",
#         "partial": 1,
#     },
#     {
#         "doctype": "{doctype_3}",
#         "strict": False,
#     },
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#     "ticket_system.auth.validate"
# ]

# Separate Database Configuration
# ------------------------------
use_separate_db = True
db_name = "ticket_system_db"
db_host = "localhost"
db_user = "ticket_system_user"
db_password = "ticket_system_password"
