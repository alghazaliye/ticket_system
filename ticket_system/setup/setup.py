import frappe
from frappe import _

def get_setup_stages():
    """
    الحصول على مراحل الإعداد
    """
    return [
        {
            "status": "الإعدادات الأساسية",
            "fail_msg": "فشل في إنشاء الإعدادات الأساسية",
            "tasks": [
                {
                    "fn": "create_default_settings",
                    "args": {},
                    "fail_msg": "فشل في إنشاء إعدادات النظام الافتراضية"
                }
            ]
        },
        {
            "status": "الأدوار والأذونات",
            "fail_msg": "فشل في إنشاء الأدوار والأذونات",
            "tasks": [
                {
                    "fn": "create_roles_and_permissions",
                    "args": {},
                    "fail_msg": "فشل في إنشاء الأدوار والأذونات"
                }
            ]
        },
        {
            "status": "البيانات الأولية",
            "fail_msg": "فشل في إنشاء البيانات الأولية",
            "tasks": [
                {
                    "fn": "create_default_cities",
                    "args": {},
                    "fail_msg": "فشل في إنشاء المدن الافتراضية"
                },
                {
                    "fn": "create_default_routes",
                    "args": {},
                    "fail_msg": "فشل في إنشاء المسارات الافتراضية"
                }
            ]
        }
    ]

@frappe.whitelist()
def setup_ticket_system():
    """
    إعداد نظام حجز التذاكر
    """
    from ticket_system.setup.install import (
        create_default_settings,
        create_roles_and_permissions,
        create_default_cities,
        create_default_routes
    )
    
    stages = get_setup_stages()
    
    # تنفيذ مراحل الإعداد
    for stage in stages:
        frappe.publish_realtime("setup_task", {"status": stage["status"], "message": "جاري التنفيذ..."})
        
        for task in stage["tasks"]:
            try:
                function = locals()[task["fn"]]
                function(**task["args"])
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("فشل في إعداد نظام حجز التذاكر"))
                frappe.publish_realtime("setup_task", {"status": stage["status"], "message": task["fail_msg"], "exception": str(e)})
                return {"status": "error", "message": task["fail_msg"]}
    
    frappe.publish_realtime("setup_task", {"status": "اكتمل", "message": "تم إعداد نظام حجز التذاكر بنجاح"})
    
    return {"status": "success", "message": "تم إعداد نظام حجز التذاكر بنجاح"}
