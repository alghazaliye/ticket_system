import frappe
from frappe import _
import random
import string

def create_booking(customer, trip, seats, agent=None, payment_method="نقداً", paid_amount=0, notes=None):
    """
    إنشاء حجز جديد
    
    المعلمات:
        customer: معرف العميل
        trip: معرف الرحلة
        seats: قائمة بالمقاعد المراد حجزها (كل مقعد يحتوي على رقم المقعد واسم الراكب ونوع الهوية ورقم الهوية)
        agent: معرف الوكيل (اختياري)
        payment_method: طريقة الدفع
        paid_amount: المبلغ المدفوع
        notes: ملاحظات
        
    العائد:
        وثيقة الحجز التي تم إنشاؤها
    """
    # التحقق من توفر المقاعد
    validate_seats_availability(trip, [seat["seat_number"] for seat in seats])
    
    # إنشاء حجز جديد
    booking = frappe.new_doc("Booking")
    booking.booking_number = generate_booking_number()
    booking.customer = customer
    booking.trip = trip
    booking.booking_date = frappe.utils.now()
    booking.payment_method = payment_method
    booking.paid_amount = paid_amount
    booking.currency = frappe.get_value("Trip", trip, "currency")
    
    if agent:
        booking.agent = agent
        # الحصول على نسبة العمولة من الوكيل
        booking.commission_rate = frappe.get_value("Agent", agent, "commission_rate")
    
    if notes:
        booking.notes = notes
    
    # إضافة المقاعد إلى الحجز
    total_amount = 0
    for seat_data in seats:
        # الحصول على سعر المقعد من حالة المقعد في الرحلة
        seat_status = get_seat_status(trip, seat_data["seat_number"])
        
        seat = frappe.new_doc("Booking Seat")
        seat.seat_number = seat_data["seat_number"]
        seat.seat_type = frappe.get_value("Seat", seat_status.seat, "seat_type")
        seat.passenger_name = seat_data["passenger_name"]
        seat.passenger_id_type = seat_data["passenger_id_type"]
        seat.passenger_id_number = seat_data["passenger_id_number"]
        seat.price = seat_status.price
        seat.status = "محجوز"
        
        booking.append("seats", seat)
        total_amount += seat_status.price
    
    # تعيين المبلغ الإجمالي
    booking.total_amount = total_amount
    
    # حساب الرصيد المتبقي
    booking.balance = total_amount - paid_amount
    
    # تعيين حالة الدفع
    if paid_amount <= 0:
        booking.payment_status = "غير مدفوع"
    elif paid_amount < total_amount:
        booking.payment_status = "مدفوع جزئياً"
    else:
        booking.payment_status = "مدفوع بالكامل"
    
    # تعيين حالة الحجز
    if booking.payment_status == "مدفوع بالكامل":
        booking.booking_status = "مؤكد"
    else:
        booking.booking_status = "مؤقت"
    
    # حساب مبلغ العمولة إذا كان هناك وكيل
    if agent and booking.commission_rate:
        booking.commission_amount = (booking.commission_rate / 100) * total_amount
    
    # حفظ الحجز
    booking.insert()
    
    # تحديث حالة المقاعد في الرحلة
    update_seat_status(trip, seats, "محجوز", booking.name)
    
    # إنشاء سجل دفع إذا كان هناك مبلغ مدفوع
    if paid_amount > 0:
        create_payment(booking.name, paid_amount, payment_method)
    
    # تقديم الحجز إذا كان مؤكداً
    if booking.booking_status == "مؤكد":
        booking.submit()
        # إنشاء تذاكر للحجز المؤكد
        create_tickets_for_booking(booking.name)
    
    return booking

def validate_seats_availability(trip, seat_numbers):
    """
    التحقق من توفر المقاعد للرحلة
    
    المعلمات:
        trip: معرف الرحلة
        seat_numbers: قائمة بأرقام المقاعد المراد التحقق منها
        
    يرفع استثناء إذا كان أي من المقاعد غير متاح
    """
    for seat_number in seat_numbers:
        seat_status = get_seat_status(trip, seat_number)
        if not seat_status or seat_status.status != "متاح":
            frappe.throw(_(f"المقعد رقم {seat_number} غير متاح للحجز"))

def get_seat_status(trip, seat_number):
    """
    الحصول على حالة المقعد في الرحلة
    
    المعلمات:
        trip: معرف الرحلة
        seat_number: رقم المقعد
        
    العائد:
        وثيقة حالة المقعد في الرحلة
    """
    # البحث عن المقعد بناءً على رقم المقعد
    seat = frappe.get_all(
        "Seat",
        filters={"seat_number": seat_number},
        fields=["name"]
    )
    
    if not seat:
        frappe.throw(_(f"المقعد رقم {seat_number} غير موجود"))
    
    # البحث عن حالة المقعد في الرحلة
    seat_status = frappe.get_all(
        "Trip Seat Status",
        filters={"trip": trip, "seat": seat[0].name},
        fields=["name", "seat", "status", "price"]
    )
    
    if not seat_status:
        frappe.throw(_(f"حالة المقعد رقم {seat_number} غير محددة للرحلة"))
    
    return frappe.get_doc("Trip Seat Status", seat_status[0].name)

def update_seat_status(trip, seats, status, booking=None):
    """
    تحديث حالة المقاعد في الرحلة
    
    المعلمات:
        trip: معرف الرحلة
        seats: قائمة بالمقاعد (كل مقعد يحتوي على رقم المقعد)
        status: الحالة الجديدة للمقاعد
        booking: معرف الحجز (مطلوب إذا كانت الحالة محجوز أو مباع)
    """
    for seat_data in seats:
        seat_status = get_seat_status(trip, seat_data["seat_number"])
        seat_status.status = status
        
        if booking and status in ["محجوز", "مباع"]:
            seat_status.booking = booking
        elif status == "متاح":
            seat_status.booking = None
        
        seat_status.save()
    
    # تحديث عدد المقاعد المتاحة في الرحلة
    update_available_seats_count(trip)

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

def create_payment(booking, amount, payment_method, transaction_id=None, notes=None):
    """
    إنشاء سجل دفع جديد
    
    المعلمات:
        booking: معرف الحجز
        amount: المبلغ المدفوع
        payment_method: طريقة الدفع
        transaction_id: معرف المعاملة (للدفع الإلكتروني)
        notes: ملاحظات
        
    العائد:
        وثيقة الدفع التي تم إنشاؤها
    """
    payment = frappe.new_doc("Payment")
    payment.payment_number = generate_payment_number()
    payment.booking = booking
    payment.payment_date = frappe.utils.now()
    payment.payment_method = payment_method
    payment.amount = amount
    payment.currency = frappe.get_value("Booking", booking, "currency")
    payment.status = "ناجح"
    payment.received_by = frappe.session.user
    
    if transaction_id:
        payment.transaction_id = transaction_id
    
    if notes:
        payment.notes = notes
    
    payment.insert()
    payment.submit()
    
    return payment

def create_tickets_for_booking(booking):
    """
    إنشاء تذاكر للحجز المؤكد
    
    المعلمات:
        booking: معرف الحجز
        
    العائد:
        قائمة بالتذاكر التي تم إنشاؤها
    """
    booking_doc = frappe.get_doc("Booking", booking)
    tickets = []
    
    for seat in booking_doc.seats:
        ticket = frappe.new_doc("Ticket")
        ticket.ticket_number = generate_ticket_number()
        ticket.trip = booking_doc.trip
        ticket.seat_number = seat.seat_number
        ticket.passenger_name = seat.passenger_name
        ticket.passenger_id_type = seat.passenger_id_type
        ticket.passenger_id_number = seat.passenger_id_number
        ticket.booking_date = booking_doc.booking_date
        ticket.issue_date = frappe.utils.now()
        ticket.price = seat.price
        ticket.currency = booking_doc.currency
        
        if booking_doc.agent:
            ticket.agent = booking_doc.agent
        
        ticket.status = "صالحة"
        ticket.insert()
        
        tickets.append(ticket)
    
    return tickets

def cancel_booking(booking, reason=None):
    """
    إلغاء الحجز
    
    المعلمات:
        booking: معرف الحجز
        reason: سبب الإلغاء
        
    العائد:
        وثيقة الحجز التي تم إلغاؤها
    """
    booking_doc = frappe.get_doc("Booking", booking)
    
    # التحقق من أن الحجز ليس ملغى بالفعل
    if booking_doc.booking_status == "ملغى":
        frappe.throw(_("الحجز ملغى بالفعل"))
    
    # تحديث حالة الحجز
    booking_doc.booking_status = "ملغى"
    
    if reason:
        booking_doc.notes = f"{booking_doc.notes or ''}\n\nسبب الإلغاء: {reason}"
    
    booking_doc.save()
    
    # إلغاء التذاكر المرتبطة بالحجز
    cancel_tickets_for_booking(booking)
    
    # تحديث حالة المقاعد في الرحلة
    seats = [{"seat_number": seat.seat_number} for seat in booking_doc.seats]
    update_seat_status(booking_doc.trip, seats, "متاح")
    
    return booking_doc

def cancel_tickets_for_booking(booking):
    """
    إلغاء التذاكر المرتبطة بالحجز
    
    المعلمات:
        booking: معرف الحجز
    """
    # البحث عن التذاكر المرتبطة بالحجز
    tickets = frappe.get_all(
        "Ticket",
        filters={"booking": booking, "status": "صالحة"},
        fields=["name"]
    )
    
    # إلغاء كل تذكرة
    for ticket in tickets:
        ticket_doc = frappe.get_doc("Ticket", ticket.name)
        ticket_doc.status = "ملغاة"
        ticket_doc.save()

def generate_booking_number():
    """
    توليد رقم حجز فريد
    
    العائد:
        رقم الحجز
    """
    prefix = "BK"
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{random_part}"

def generate_payment_number():
    """
    توليد رقم دفع فريد
    
    العائد:
        رقم الدفع
    """
    prefix = "PAY"
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{random_part}"

def generate_ticket_number():
    """
    توليد رقم تذكرة فريد
    
    العائد:
        رقم التذكرة
    """
    prefix = "TKT"
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{random_part}"
