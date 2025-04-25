import frappe
from frappe import _
import json

def get_agent_details(agent):
    """
    الحصول على تفاصيل الوكيل
    
    المعلمات:
        agent: معرف الوكيل
        
    العائد:
        تفاصيل الوكيل مع معلومات المبيعات والعمولات
    """
    # الحصول على معلومات الوكيل
    agent_doc = frappe.get_doc("Agent", agent)
    
    # الحصول على إحصائيات المبيعات
    sales_stats = get_agent_sales_statistics(agent)
    
    # إنشاء قاموس بتفاصيل الوكيل
    agent_details = {
        "agent": agent_doc,
        "sales_statistics": sales_stats
    }
    
    return agent_details

def get_agent_sales_statistics(agent):
    """
    الحصول على إحصائيات مبيعات الوكيل
    
    المعلمات:
        agent: معرف الوكيل
        
    العائد:
        إحصائيات المبيعات (عدد الحجوزات، إجمالي المبيعات، إجمالي العمولات)
    """
    # الحصول على جميع الحجوزات للوكيل
    bookings = frappe.get_all(
        "Booking",
        filters={"agent": agent, "booking_status": ["!=", "ملغى"]},
        fields=["name", "total_amount", "commission_amount", "booking_status"]
    )
    
    # حساب الإحصائيات
    total_bookings = len(bookings)
    total_sales = sum(booking.total_amount for booking in bookings)
    total_commission = sum(booking.commission_amount or 0 for booking in bookings)
    
    # تصنيف الحجوزات حسب الحالة
    confirmed_bookings = len([b for b in bookings if b.booking_status == "مؤكد"])
    pending_bookings = len([b for b in bookings if b.booking_status == "مؤقت"])
    
    # الحصول على عدد التذاكر المباعة
    tickets = frappe.get_all(
        "Ticket",
        filters={"agent": agent, "status": ["!=", "ملغاة"]},
        fields=["name"]
    )
    
    total_tickets = len(tickets)
    
    return {
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "pending_bookings": pending_bookings,
        "total_tickets": total_tickets,
        "total_sales": total_sales,
        "total_commission": total_commission
    }

def get_agent_account_statement(agent, from_date=None, to_date=None):
    """
    الحصول على كشف حساب الوكيل
    
    المعلمات:
        agent: معرف الوكيل
        from_date: تاريخ البداية
        to_date: تاريخ النهاية
        
    العائد:
        كشف حساب الوكيل (قائمة بالمعاملات، الرصيد الافتتاحي، الرصيد الختامي)
    """
    filters = {"agent": agent}
    
    if from_date:
        filters["booking_date"] = [">=", from_date]
    
    if to_date:
        if "booking_date" in filters:
            filters["booking_date"] = ["between", [from_date, to_date]]
        else:
            filters["booking_date"] = ["<=", to_date]
    
    # الحصول على جميع الحجوزات للوكيل خلال الفترة المحددة
    bookings = frappe.get_all(
        "Booking",
        filters=filters,
        fields=["name", "booking_number", "booking_date", "total_amount", "commission_amount", "booking_status"],
        order_by="booking_date"
    )
    
    # الحصول على جميع المدفوعات للوكيل خلال الفترة المحددة
    payment_filters = {"agent": agent}
    
    if from_date:
        payment_filters["payment_date"] = [">=", from_date]
    
    if to_date:
        if "payment_date" in payment_filters:
            payment_filters["payment_date"] = ["between", [from_date, to_date]]
        else:
            payment_filters["payment_date"] = ["<=", to_date]
    
    payments = frappe.get_all(
        "Agent Payment",
        filters=payment_filters,
        fields=["name", "payment_number", "payment_date", "amount", "payment_type"],
        order_by="payment_date"
    )
    
    # دمج الحجوزات والمدفوعات في قائمة واحدة مرتبة حسب التاريخ
    transactions = []
    
    for booking in bookings:
        transactions.append({
            "date": booking.booking_date,
            "type": "حجز",
            "reference": booking.booking_number,
            "description": f"حجز رقم {booking.booking_number}",
            "debit": booking.total_amount,
            "credit": 0,
            "commission": booking.commission_amount or 0,
            "status": booking.booking_status
        })
    
    for payment in payments:
        transactions.append({
            "date": payment.payment_date,
            "type": "دفعة",
            "reference": payment.payment_number,
            "description": f"دفعة رقم {payment.payment_number} ({payment.payment_type})",
            "debit": 0,
            "credit": payment.amount,
            "commission": 0,
            "status": "مكتمل"
        })
    
    # ترتيب المعاملات حسب التاريخ
    transactions.sort(key=lambda x: x["date"])
    
    # حساب الرصيد الافتتاحي
    opening_balance = get_agent_balance_at_date(agent, from_date) if from_date else 0
    
    # حساب الرصيد لكل معاملة
    balance = opening_balance
    
    for transaction in transactions:
        balance = balance + transaction["debit"] - transaction["credit"]
        transaction["balance"] = balance
    
    # حساب إجماليات الكشف
    total_debit = sum(transaction["debit"] for transaction in transactions)
    total_credit = sum(transaction["credit"] for transaction in transactions)
    total_commission = sum(transaction["commission"] for transaction in transactions)
    closing_balance = opening_balance + total_debit - total_credit
    
    return {
        "agent": frappe.get_doc("Agent", agent),
        "from_date": from_date,
        "to_date": to_date,
        "opening_balance": opening_balance,
        "transactions": transactions,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "total_commission": total_commission,
        "closing_balance": closing_balance
    }

def get_agent_balance_at_date(agent, date):
    """
    الحصول على رصيد الوكيل في تاريخ محدد
    
    المعلمات:
        agent: معرف الوكيل
        date: التاريخ
        
    العائد:
        رصيد الوكيل في التاريخ المحدد
    """
    # الحصول على جميع الحجوزات للوكيل قبل التاريخ المحدد
    bookings = frappe.get_all(
        "Booking",
        filters={"agent": agent, "booking_date": ["<", date]},
        fields=["total_amount"]
    )
    
    # الحصول على جميع المدفوعات للوكيل قبل التاريخ المحدد
    payments = frappe.get_all(
        "Agent Payment",
        filters={"agent": agent, "payment_date": ["<", date]},
        fields=["amount"]
    )
    
    # حساب الرصيد
    total_bookings = sum(booking.total_amount for booking in bookings)
    total_payments = sum(payment.amount for payment in payments)
    
    return total_bookings - total_payments

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
    # التحقق من وجود الوكيل
    agent_doc = frappe.get_doc("Agent", agent)
    
    # إنشاء دفعة جديدة
    payment = frappe.new_doc("Agent Payment")
    payment.payment_number = generate_payment_number()
    payment.agent = agent
    payment.payment_date = frappe.utils.now()
    payment.amount = amount
    payment.payment_type = payment_type
    payment.payment_method = payment_method
    
    if reference:
        payment.reference = reference
    
    if notes:
        payment.notes = notes
    
    payment.insert()
    payment.submit()
    
    # تحديث رصيد الوكيل
    update_agent_balance(agent)
    
    return payment

def update_agent_balance(agent):
    """
    تحديث رصيد الوكيل
    
    المعلمات:
        agent: معرف الوكيل
    """
    # الحصول على جميع الحجوزات للوكيل
    bookings = frappe.get_all(
        "Booking",
        filters={"agent": agent, "booking_status": ["!=", "ملغى"]},
        fields=["total_amount"]
    )
    
    # الحصول على جميع المدفوعات للوكيل
    payments = frappe.get_all(
        "Agent Payment",
        filters={"agent": agent, "docstatus": 1},
        fields=["amount"]
    )
    
    # حساب الرصيد
    total_bookings = sum(booking.total_amount for booking in bookings)
    total_payments = sum(payment.amount for payment in payments)
    current_balance = total_bookings - total_payments
    
    # تحديث رصيد الوكيل
    frappe.db.set_value("Agent", agent, "current_balance", current_balance)
    
    return current_balance

def generate_payment_number():
    """
    توليد رقم دفعة فريد
    
    العائد:
        رقم الدفعة
    """
    import random
    import string
    
    prefix = "AGP"
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{random_part}"
