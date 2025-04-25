import frappe
from frappe import _
import qrcode
import os
import random
import string
from io import BytesIO

def get_ticket_details(ticket):
    """
    الحصول على تفاصيل التذكرة
    
    المعلمات:
        ticket: معرف التذكرة
        
    العائد:
        تفاصيل التذكرة مع معلومات الرحلة والمقعد
    """
    # الحصول على معلومات التذكرة
    ticket_doc = frappe.get_doc("Ticket", ticket)
    
    # الحصول على معلومات الرحلة
    trip = frappe.get_doc("Trip", ticket_doc.trip)
    
    # الحصول على معلومات المسار
    route = frappe.get_doc("Route", trip.route)
    
    # إنشاء قاموس بتفاصيل التذكرة
    ticket_details = {
        "ticket": ticket_doc,
        "trip": trip,
        "route": route,
        "from_city_name": frappe.get_value("City", route.from_city, "city_name"),
        "to_city_name": frappe.get_value("City", route.to_city, "city_name")
    }
    
    return ticket_details

def validate_ticket(ticket_number):
    """
    التحقق من صلاحية التذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        حالة التحقق (صالحة، مستخدمة، ملغاة، غير موجودة)
        تفاصيل التذكرة إذا كانت موجودة
    """
    # البحث عن التذكرة
    tickets = frappe.get_all(
        "Ticket",
        filters={"ticket_number": ticket_number},
        fields=["name", "status"]
    )
    
    if not tickets:
        return {"status": "غير موجودة", "message": "التذكرة غير موجودة"}
    
    ticket = frappe.get_doc("Ticket", tickets[0].name)
    
    if ticket.status == "صالحة":
        # التحقق من تاريخ الرحلة
        trip = frappe.get_doc("Trip", ticket.trip)
        
        if frappe.utils.getdate(trip.trip_date) < frappe.utils.getdate():
            return {"status": "منتهية", "message": "تاريخ الرحلة انتهى", "ticket": ticket}
        
        return {"status": "صالحة", "message": "التذكرة صالحة", "ticket": ticket}
    elif ticket.status == "مستخدمة":
        return {"status": "مستخدمة", "message": "التذكرة مستخدمة بالفعل", "ticket": ticket}
    elif ticket.status == "ملغاة":
        return {"status": "ملغاة", "message": "التذكرة ملغاة", "ticket": ticket}
    
    return {"status": "غير معروفة", "message": "حالة التذكرة غير معروفة", "ticket": ticket}

def mark_ticket_as_used(ticket_number):
    """
    تحديد التذكرة كمستخدمة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        حالة العملية (نجاح، فشل)
        رسالة توضيحية
    """
    # التحقق من صلاحية التذكرة
    validation = validate_ticket(ticket_number)
    
    if validation["status"] != "صالحة":
        return {"status": "فشل", "message": validation["message"]}
    
    # تحديث حالة التذكرة
    ticket = validation["ticket"]
    ticket.status = "مستخدمة"
    ticket.save()
    
    return {"status": "نجاح", "message": "تم تحديد التذكرة كمستخدمة بنجاح"}

def cancel_ticket(ticket_number, reason=None):
    """
    إلغاء التذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        reason: سبب الإلغاء
        
    العائد:
        حالة العملية (نجاح، فشل)
        رسالة توضيحية
    """
    # البحث عن التذكرة
    tickets = frappe.get_all(
        "Ticket",
        filters={"ticket_number": ticket_number},
        fields=["name", "status"]
    )
    
    if not tickets:
        return {"status": "فشل", "message": "التذكرة غير موجودة"}
    
    ticket = frappe.get_doc("Ticket", tickets[0].name)
    
    if ticket.status == "ملغاة":
        return {"status": "فشل", "message": "التذكرة ملغاة بالفعل"}
    
    if ticket.status == "مستخدمة":
        return {"status": "فشل", "message": "لا يمكن إلغاء تذكرة مستخدمة"}
    
    # تحديث حالة التذكرة
    ticket.status = "ملغاة"
    
    if reason:
        ticket.notes = f"{ticket.notes or ''}\n\nسبب الإلغاء: {reason}"
    
    ticket.save()
    
    # تحديث حالة المقعد في الرحلة
    update_seat_status_for_ticket(ticket)
    
    return {"status": "نجاح", "message": "تم إلغاء التذكرة بنجاح"}

def update_seat_status_for_ticket(ticket):
    """
    تحديث حالة المقعد في الرحلة بناءً على حالة التذكرة
    
    المعلمات:
        ticket: وثيقة التذكرة
    """
    # البحث عن حالة المقعد في الرحلة
    seat = frappe.get_all(
        "Seat",
        filters={"seat_number": ticket.seat_number},
        fields=["name"]
    )
    
    if not seat:
        return
    
    seat_status = frappe.get_all(
        "Trip Seat Status",
        filters={"trip": ticket.trip, "seat": seat[0].name},
        fields=["name"]
    )
    
    if not seat_status:
        return
    
    # تحديث حالة المقعد
    seat_status_doc = frappe.get_doc("Trip Seat Status", seat_status[0].name)
    
    if ticket.status == "صالحة":
        seat_status_doc.status = "مباع"
    elif ticket.status == "ملغاة":
        seat_status_doc.status = "متاح"
        seat_status_doc.booking = None
    
    seat_status_doc.save()
    
    # تحديث عدد المقاعد المتاحة في الرحلة
    update_available_seats_count(ticket.trip)

def update_available_seats_count(trip):
    """
    تحديث عدد المقاعد المتاحة في الرحلة
    
    المعلمات:
        trip: معرف الرحلة
    """
    # حساب عدد المقاعد المتاحة
    available_seats_count = frappe.db.count(
        "Trip Seat Status",
        filters={"trip": trip, "status": "متاح"}
    )
    
    # تحديث عدد المقاعد المتاحة في الرحلة
    frappe.db.set_value("Trip", trip, "available_seats", available_seats_count)

def generate_qr_code(ticket_number):
    """
    توليد رمز QR للتذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        مسار ملف رمز QR
    """
    # إنشاء رمز QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(ticket_number)
    qr.make(fit=True)
    
    # إنشاء صورة
    img = qr.make_image(fill_color="black", back_color="white")
    
    # حفظ الصورة في ذاكرة مؤقتة
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # حفظ الصورة في ملف
    file_name = f"ticket_qr_{ticket_number}.png"
    file_path = os.path.join("/tmp", file_name)
    
    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())
    
    return file_path

def print_ticket(ticket_number):
    """
    طباعة التذكرة
    
    المعلمات:
        ticket_number: رقم التذكرة
        
    العائد:
        مسار ملف PDF للتذكرة
    """
    # التحقق من وجود التذكرة
    tickets = frappe.get_all(
        "Ticket",
        filters={"ticket_number": ticket_number},
        fields=["name"]
    )
    
    if not tickets:
        frappe.throw(_("التذكرة غير موجودة"))
    
    # الحصول على تفاصيل التذكرة
    ticket_details = get_ticket_details(tickets[0].name)
    
    # توليد رمز QR
    qr_path = generate_qr_code(ticket_number)
    
    # إنشاء ملف HTML للتذكرة
    html = frappe.render_template(
        "ticket_system/templates/ticket_template.html",
        {"ticket": ticket_details, "qr_path": qr_path}
    )
    
    # تحويل HTML إلى PDF
    pdf_path = f"/tmp/ticket_{ticket_number}.pdf"
    
    # استخدام wkhtmltopdf لتحويل HTML إلى PDF
    # هذا مثال بسيط، في التطبيق الحقيقي يمكن استخدام مكتبات أكثر تقدماً
    with open(f"/tmp/ticket_{ticket_number}.html", "w") as f:
        f.write(html)
    
    os.system(f"wkhtmltopdf /tmp/ticket_{ticket_number}.html {pdf_path}")
    
    return pdf_path
