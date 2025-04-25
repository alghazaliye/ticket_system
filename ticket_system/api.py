import frappe
from frappe import _
from ticket_system.reports.reports import (
    get_sales_report,
    get_trips_report,
    get_agents_performance_report,
    get_financial_report,
    get_dashboard_data,
    export_report_to_csv,
    export_report_to_pdf
)

@frappe.whitelist()
def search_trips(source_city, destination_city, trip_date, vehicle_type=None):
    """
    البحث عن الرحلات المتاحة
    
    المعلمات:
        source_city: المدينة المصدر
        destination_city: المدينة الوجهة
        trip_date: تاريخ الرحلة
        vehicle_type: نوع المركبة (اختياري)
        
    العائد:
        قائمة بالرحلات المتاحة
    """
    from ticket_system.controllers.trip_controller import search_trips as search_trips_controller
    return search_trips_controller(source_city, destination_city, trip_date, vehicle_type)

@frappe.whitelist()
def get_available_destinations(from_city):
    """
    الحصول على الوجهات المتاحة من مدينة معينة
    
    المعلمات:
        from_city: المدينة المصدر
        
    العائد:
        قائمة بالوجهات المتاحة
    """
    from ticket_system.controllers.trip_controller import get_available_destinations as get_available_destinations_controller
    return get_available_destinations_controller(from_city)

@frappe.whitelist()
def get_trip_details(trip):
    """
    الحصول على تفاصيل الرحلة
    
    المعلمات:
        trip: معرف الرحلة
        
    العائد:
        تفاصيل الرحلة
    """
    from ticket_system.controllers.trip_controller import get_trip_details as get_trip_details_controller
    return get_trip_details_controller(trip)

@frappe.whitelist()
def get_available_seats(trip):
    """
    الحصول على المقاعد المتاحة في الرحلة
    
    المعلمات:
        trip: معرف الرحلة
        
    العائد:
        قائمة بالمقاعد المتاحة
    """
    from ticket_system.controllers.trip_controller import get_available_seats as get_available_seats_controller
    return get_available_seats_controller(trip)

@frappe.whitelist()
def create_booking(customer, trip, seats, agent=None, payment_method=None, paid_amount=0, notes=None):
    """
    إنشاء حجز جديد
    
    المعلمات:
        customer: معرف العميل
        trip: معرف الرحلة
        seats: قائمة بالمقاعد المحجوزة
        agent: معرف الوكيل (اختياري)
        payment_method: طريقة الدفع (اختياري)
        paid_amount: المبلغ المدفوع (اختياري)
        notes: ملاحظات (اختياري)
        
    العائد:
        وثيقة الحجز التي تم إنشاؤها
    """
    from ticket_system.controllers.booking_controller import create_booking as create_booking_controller
    return create_booking_controller(customer, trip, seats, agent, payment_method, paid_amount, notes)

@frappe.whitelist()
def cancel_booking(booking, reason=None):
    """
    إلغاء حجز
    
    المعلمات:
        booking: معرف الحجز
        reason: سبب الإلغاء (اختياري)
        
    العائد:
        حالة العملية (نجاح، فشل)
        رسالة توضيحية
    """
    from ticket_system.controllers.booking_controller import cancel_booking as cancel_booking_controller
    return cancel_booking_controller(booking, reason)

@frappe.whitelist()
def get_booking_details(booking):
    """
    الحصول على تفاصيل الحجز
    
    المعلمات:
        booking: معرف الحجز
        
    العائد:
        تفاصيل الحجز
    """
    from ticket_system.controllers.booking_controller import get_booking_details as get_booking_details_controller
    return get_booking_details_controller(booking)

@frappe.whitelist()
def get_ticket_details(ticket):
    """
    الحصول على تفاصيل التذكرة
    
    المعلمات:
        ticket: معرف التذكرة
        
    العائد:
        تفاصيل التذكرة
    """
    from ticket_system.controllers.ticket_controller import get_ticket_details as get_ticket_details_controller
    return get_ticket_details_controller(ticket)

@frappe.whitelist()
def validate_ticket(ticket_number):
    """
    التحقق من صلاحية التذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        حالة التحقق (صالحة، مستخدمة، ملغاة، غير موجودة)
        تفاصيل التذكرة إذا كانت موجودة
    """
    from ticket_system.controllers.ticket_controller import validate_ticket as validate_ticket_controller
    return validate_ticket_controller(ticket_number)

@frappe.whitelist()
def mark_ticket_as_used(ticket_number):
    """
    تحديد التذكرة كمستخدمة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        حالة العملية (نجاح، فشل)
        رسالة توضيحية
    """
    from ticket_system.controllers.ticket_controller import mark_ticket_as_used as mark_ticket_as_used_controller
    return mark_ticket_as_used_controller(ticket_number)

@frappe.whitelist()
def cancel_ticket(ticket_number, reason=None):
    """
    إلغاء التذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        reason: سبب الإلغاء (اختياري)
        
    العائد:
        حالة العملية (نجاح، فشل)
        رسالة توضيحية
    """
    from ticket_system.controllers.ticket_controller import cancel_ticket as cancel_ticket_controller
    return cancel_ticket_controller(ticket_number, reason)

@frappe.whitelist()
def print_ticket(ticket_number):
    """
    طباعة التذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        مسار ملف PDF للتذكرة
    """
    from ticket_system.controllers.ticket_controller import print_ticket as print_ticket_controller
    return print_ticket_controller(ticket_number)

@frappe.whitelist()
def get_agent_details(agent):
    """
    الحصول على تفاصيل الوكيل
    
    المعلمات:
        agent: معرف الوكيل
        
    العائد:
        تفاصيل الوكيل مع معلومات المبيعات والعمولات
    """
    from ticket_system.controllers.agent_controller import get_agent_details as get_agent_details_controller
    return get_agent_details_controller(agent)

@frappe.whitelist()
def get_agent_account_statement(agent, from_date=None, to_date=None):
    """
    الحصول على كشف حساب الوكيل
    
    المعلمات:
        agent: معرف الوكيل
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        
    العائد:
        كشف حساب الوكيل
    """
    from ticket_system.controllers.agent_controller import get_agent_account_statement as get_agent_account_statement_controller
    return get_agent_account_statement_controller(agent, from_date, to_date)

@frappe.whitelist()
def create_agent_payment(agent, amount, payment_type, payment_method, reference=None, notes=None):
    """
    إنشاء دفعة للوكيل
    
    المعلمات:
        agent: معرف الوكيل
        amount: المبلغ
        payment_type: نوع الدفعة (تسوية، دفعة مقدمة، استرداد)
        payment_method: طريقة الدفع (نقداً، تحويل بنكي، شيك)
        reference: مرجع الدفعة (اختياري)
        notes: ملاحظات (اختياري)
        
    العائد:
        وثيقة الدفعة التي تم إنشاؤها
    """
    from ticket_system.controllers.agent_controller import create_agent_payment as create_agent_payment_controller
    return create_agent_payment_controller(agent, amount, payment_type, payment_method, reference, notes)

@frappe.whitelist()
def get_sales_report_api(from_date=None, to_date=None, agent=None, route=None, export_format=None):
    """
    الحصول على تقرير المبيعات
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        agent: معرف الوكيل (اختياري)
        route: معرف المسار (اختياري)
        export_format: تنسيق التصدير (csv, pdf) (اختياري)
        
    العائد:
        تقرير المبيعات أو مسار الملف المصدر
    """
    report = get_sales_report(from_date, to_date, agent, route)
    
    if export_format == "csv":
        return export_report_to_csv(report, "sales")
    elif export_format == "pdf":
        return export_report_to_pdf(report, "sales")
    
    return report

@frappe.whitelist()
def get_trips_report_api(from_date=None, to_date=None, route=None, vehicle_type=None, export_format=None):
    """
    الحصول على تقرير الرحلات
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        route: معرف المسار (اختياري)
        vehicle_type: نوع المركبة (اختياري)
        export_format: تنسيق التصدير (csv, pdf) (اختياري)
        
    العائد:
        تقرير الرحلات أو مسار الملف المصدر
    """
    report = get_trips_report(from_date, to_date, route, vehicle_type)
    
    if export_format == "csv":
        return export_report_to_csv(report, "trips")
    elif export_format == "pdf":
        return export_report_to_pdf(report, "trips")
    
    return report

@frappe.whitelist()
def get_agents_performance_report_api(from_date=None, to_date=None, export_format=None):
    """
    الحصول على تقرير أداء الوكلاء
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        export_format: تنسيق التصدير (csv, pdf) (اختياري)
        
    العائد:
        تقرير أداء الوكلاء أو مسار الملف المصدر
    """
    report = get_agents_performance_report(from_date, to_date)
    
    if export_format == "csv":
        return export_report_to_csv(report, "agents")
    elif export_format == "pdf":
        return export_report_to_pdf(report, "agents")
    
    return report

@frappe.whitelist()
def get_financial_report_api(from_date=None, to_date=None, export_format=None):
    """
    الحصول على التقرير المالي
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        export_format: تنسيق التصدير (csv, pdf) (اختياري)
        
    العائد:
        التقرير المالي أو مسار الملف المصدر
    """
    report = get_financial_report(from_date, to_date)
    
    if export_format == "csv":
        return export_report_to_csv(report, "financial")
    elif export_format == "pdf":
        return export_report_to_pdf(report, "financial")
    
    return report

@frappe.whitelist()
def get_dashboard_data_api(period="today"):
    """
    الحصول على بيانات لوحة التحكم
    
    المعلمات:
        period: الفترة الزمنية (today, yesterday, this_week, this_month, last_month, this_year)
        
    العائد:
        بيانات لوحة التحكم
    """
    return get_dashboard_data(period)
