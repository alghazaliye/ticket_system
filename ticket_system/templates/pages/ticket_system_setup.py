import frappe
from frappe import _

def get_context(context):
    """
    الحصول على سياق صفحة الإعداد
    """
    context.no_cache = 1
    context.show_sidebar = True
    context.title = _("إعداد نظام حجز التذاكر")
    
    context.setup_stages = [
        {"name": "الإعدادات الأساسية", "status": "pending", "icon": "fa fa-cog"},
        {"name": "الأدوار والأذونات", "status": "pending", "icon": "fa fa-lock"},
        {"name": "البيانات الأولية", "status": "pending", "icon": "fa fa-database"}
    ]
    
    return context

@frappe.whitelist()
def run_setup():
    """
    تشغيل عملية الإعداد
    """
    from ticket_system.setup.setup import setup_ticket_system
    return setup_ticket_system()
