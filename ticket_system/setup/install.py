import frappe
from frappe import _

def after_install():
    """
    تنفيذ الإجراءات اللازمة بعد تثبيت التطبيق
    """
    # إنشاء إعدادات النظام الافتراضية
    create_default_settings()
    
    # إنشاء الأدوار والأذونات
    create_roles_and_permissions()
    
    # إنشاء البيانات الأولية
    create_initial_data()
    
    frappe.msgprint(_("تم تثبيت نظام حجز التذاكر بنجاح!"))

def create_default_settings():
    """
    إنشاء إعدادات النظام الافتراضية
    """
    if not frappe.db.exists("Ticket System Settings"):
        settings = frappe.new_doc("Ticket System Settings")
        settings.company_name = frappe.defaults.get_global_default("company") or "شركة النقل"
        settings.default_currency = frappe.defaults.get_global_default("currency") or "ريال"
        settings.default_agent_commission_rate = 5.0
        settings.enable_tax = 0
        settings.tax_rate = 0.0
        settings.insert()

def create_roles_and_permissions():
    """
    إنشاء الأدوار والأذونات
    """
    # إنشاء الأدوار
    roles = [
        "Ticket System Manager",
        "Ticket System User",
        "Ticket System Agent",
        "Ticket System Reports"
    ]
    
    for role in roles:
        if not frappe.db.exists("Role", role):
            role_doc = frappe.new_doc("Role")
            role_doc.role_name = role
            role_doc.desk_access = 1
            role_doc.insert()
    
    # تعيين الأذونات (يتم تعريفها في ملفات JSON للـ DocTypes)

def create_initial_data():
    """
    إنشاء البيانات الأولية
    """
    # إنشاء المدن الافتراضية
    create_default_cities()
    
    # إنشاء المسارات الافتراضية
    create_default_routes()

def create_default_cities():
    """
    إنشاء المدن الافتراضية
    """
    default_cities = [
        {"city_name": "الرياض", "city_code": "RUH"},
        {"city_name": "جدة", "city_code": "JED"},
        {"city_name": "الدمام", "city_code": "DMM"},
        {"city_name": "مكة المكرمة", "city_code": "MKH"},
        {"city_name": "المدينة المنورة", "city_code": "MED"}
    ]
    
    for city_data in default_cities:
        if not frappe.db.exists("City", {"city_code": city_data["city_code"]}):
            city = frappe.new_doc("City")
            city.city_name = city_data["city_name"]
            city.city_code = city_data["city_code"]
            city.insert()

def create_default_routes():
    """
    إنشاء المسارات الافتراضية
    """
    # التأكد من وجود المدن قبل إنشاء المسارات
    cities = frappe.get_all("City", fields=["name", "city_code"])
    
    if len(cities) < 2:
        return
    
    # إنشاء مسارات بين المدن
    city_map = {city.city_code: city.name for city in cities}
    
    default_routes = [
        {"from_city": "RUH", "to_city": "JED", "distance": 949, "duration": "10:30"},
        {"from_city": "RUH", "to_city": "DMM", "distance": 395, "duration": "4:15"},
        {"from_city": "RUH", "to_city": "MKH", "distance": 870, "duration": "9:00"},
        {"from_city": "RUH", "to_city": "MED", "distance": 848, "duration": "9:30"},
        {"from_city": "JED", "to_city": "RUH", "distance": 949, "duration": "10:30"},
        {"from_city": "JED", "to_city": "MKH", "distance": 79, "duration": "1:15"},
        {"from_city": "JED", "to_city": "MED", "distance": 420, "duration": "4:30"},
        {"from_city": "DMM", "to_city": "RUH", "distance": 395, "duration": "4:15"},
        {"from_city": "MKH", "to_city": "RUH", "distance": 870, "duration": "9:00"},
        {"from_city": "MKH", "to_city": "JED", "distance": 79, "duration": "1:15"},
        {"from_city": "MKH", "to_city": "MED", "distance": 450, "duration": "5:00"},
        {"from_city": "MED", "to_city": "RUH", "distance": 848, "duration": "9:30"},
        {"from_city": "MED", "to_city": "JED", "distance": 420, "duration": "4:30"},
        {"from_city": "MED", "to_city": "MKH", "distance": 450, "duration": "5:00"}
    ]
    
    for route_data in default_routes:
        from_city = city_map.get(route_data["from_city"])
        to_city = city_map.get(route_data["to_city"])
        
        if from_city and to_city and not frappe.db.exists("Route", {"from_city": from_city, "to_city": to_city}):
            route = frappe.new_doc("Route")
            route.from_city = from_city
            route.to_city = to_city
            route.distance = route_data["distance"]
            route.duration = route_data["duration"]
            route.insert()
