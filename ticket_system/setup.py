import frappe
from frappe import _
import os

def before_install():
    """
    Run before the ticket system is installed.
    This function checks prerequisites and prepares the environment.
    """
    frappe.log_error("Installing Ticket System...")
    
    # Check if we have the required permissions
    if not frappe.has_permission("System Settings", "write"):
        frappe.throw(_("Administrator privileges required for installation"))
    
    # Create necessary directories if they don't exist
    create_directories()

def after_install():
    """
    Run after the ticket system is installed.
    This function sets up initial data and configurations.
    """
    # Create default roles
    create_roles()
    
    # Create default doctypes
    create_doctypes()
    
    # Create default workflows
    create_workflows()
    
    # Create demo data if requested
    if frappe.conf.get("create_demo_data"):
        create_demo_data()
    
    frappe.log_error("Ticket System installation completed successfully!")

def before_uninstall():
    """
    Run before the ticket system is uninstalled.
    This function performs cleanup operations.
    """
    frappe.log_error("Uninstalling Ticket System...")

def after_uninstall():
    """
    Run after the ticket system is uninstalled.
    This function performs final cleanup operations.
    """
    frappe.log_error("Ticket System uninstallation completed!")

def create_directories():
    """Create necessary directories for the ticket system."""
    directories = [
        os.path.join(frappe.local.site_path, "private", "ticket_system"),
        os.path.join(frappe.local.site_path, "private", "ticket_system", "tickets"),
        os.path.join(frappe.local.site_path, "private", "ticket_system", "reports")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def create_roles():
    """Create default roles for the ticket system."""
    roles = [
        {"role_name": "Ticket Manager", "desk_access": 1},
        {"role_name": "Ticket Agent", "desk_access": 1},
        {"role_name": "Booking Staff", "desk_access": 1},
        {"role_name": "Ticket Viewer", "desk_access": 1}
    ]
    
    for role in roles:
        if not frappe.db.exists("Role", role["role_name"]):
            doc = frappe.new_doc("Role")
            doc.update(role)
            doc.insert(ignore_permissions=True)

def create_doctypes():
    """Create default doctypes for the ticket system."""
    # This will be handled by the migrations
    pass

def create_workflows():
    """Create default workflows for the ticket system."""
    # This will be handled by the migrations
    pass

def create_demo_data():
    """Create demo data for the ticket system."""
    from ticket_system.setup.demo_data import create_demo_data
    create_demo_data()

def setup_separate_database():
    """Setup separate database for the ticket system."""
    # This is handled by the Frappe framework based on hooks.py configuration
    pass
