import frappe
from frappe import _
import json
import datetime
import calendar
from dateutil.relativedelta import relativedelta

def get_sales_report(from_date=None, to_date=None, agent=None, route=None):
    """
    الحصول على تقرير المبيعات
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        agent: معرف الوكيل (اختياري)
        route: معرف المسار (اختياري)
        
    العائد:
        تقرير المبيعات مع إحصائيات وتفاصيل المبيعات
    """
    filters = {}
    
    if from_date:
        filters["booking_date"] = [">=", from_date]
    
    if to_date:
        if "booking_date" in filters:
            filters["booking_date"] = ["between", [from_date, to_date]]
        else:
            filters["booking_date"] = ["<=", to_date]
    
    if agent:
        filters["agent"] = agent
    
    # الحصول على الحجوزات
    bookings = frappe.get_all(
        "Booking",
        filters=filters,
        fields=["name", "booking_number", "booking_date", "customer", "agent", 
                "total_amount", "paid_amount", "booking_status", "payment_status"]
    )
    
    # الحصول على تفاصيل التذاكر لكل حجز
    booking_details = []
    
    for booking in bookings:
        # الحصول على تفاصيل العميل
        customer_name = frappe.get_value("Customer", booking.customer, "customer_name")
        
        # الحصول على تفاصيل الوكيل
        agent_name = None
        if booking.agent:
            agent_name = frappe.get_value("Agent", booking.agent, "agent_name")
        
        # الحصول على التذاكر المرتبطة بالحجز
        tickets = frappe.get_all(
            "Ticket",
            filters={"booking": booking.name},
            fields=["name", "ticket_number", "passenger_name", "trip", "seat_number", "price", "status"]
        )
        
        # الحصول على تفاصيل الرحلات للتذاكر
        for ticket in tickets:
            trip = frappe.get_doc("Trip", ticket.trip)
            route_doc = frappe.get_doc("Route", trip.route)
            
            # تخطي التذكرة إذا كان هناك تصفية حسب المسار
            if route and trip.route != route:
                continue
            
            from_city_name = frappe.get_value("City", route_doc.from_city, "city_name")
            to_city_name = frappe.get_value("City", route_doc.to_city, "city_name")
            
            booking_details.append({
                "booking_number": booking.booking_number,
                "booking_date": booking.booking_date,
                "customer_name": customer_name,
                "agent_name": agent_name,
                "ticket_number": ticket.ticket_number,
                "passenger_name": ticket.passenger_name,
                "trip_code": trip.trip_code,
                "trip_date": trip.trip_date,
                "from_city": from_city_name,
                "to_city": to_city_name,
                "seat_number": ticket.seat_number,
                "price": ticket.price,
                "status": ticket.status
            })
    
    # حساب الإحصائيات
    total_bookings = len(set(detail["booking_number"] for detail in booking_details))
    total_tickets = len(booking_details)
    total_sales = sum(detail["price"] for detail in booking_details)
    
    # تصنيف المبيعات حسب المسار
    sales_by_route = {}
    for detail in booking_details:
        route_name = f"{detail['from_city']} - {detail['to_city']}"
        if route_name not in sales_by_route:
            sales_by_route[route_name] = {
                "count": 0,
                "amount": 0
            }
        
        sales_by_route[route_name]["count"] += 1
        sales_by_route[route_name]["amount"] += detail["price"]
    
    # تصنيف المبيعات حسب التاريخ
    sales_by_date = {}
    for detail in booking_details:
        booking_date = detail["booking_date"].strftime("%Y-%m-%d")
        if booking_date not in sales_by_date:
            sales_by_date[booking_date] = {
                "count": 0,
                "amount": 0
            }
        
        sales_by_date[booking_date]["count"] += 1
        sales_by_date[booking_date]["amount"] += detail["price"]
    
    # تصنيف المبيعات حسب الوكيل
    sales_by_agent = {}
    for detail in booking_details:
        if not detail["agent_name"]:
            agent_name = "مباشر"
        else:
            agent_name = detail["agent_name"]
        
        if agent_name not in sales_by_agent:
            sales_by_agent[agent_name] = {
                "count": 0,
                "amount": 0
            }
        
        sales_by_agent[agent_name]["count"] += 1
        sales_by_agent[agent_name]["amount"] += detail["price"]
    
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_bookings": total_bookings,
        "total_tickets": total_tickets,
        "total_sales": total_sales,
        "sales_by_route": sales_by_route,
        "sales_by_date": sales_by_date,
        "sales_by_agent": sales_by_agent,
        "details": booking_details
    }

def get_trips_report(from_date=None, to_date=None, route=None, vehicle_type=None):
    """
    الحصول على تقرير الرحلات
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        route: معرف المسار (اختياري)
        vehicle_type: نوع المركبة (اختياري)
        
    العائد:
        تقرير الرحلات مع إحصائيات وتفاصيل الرحلات
    """
    filters = {}
    
    if from_date:
        filters["trip_date"] = [">=", from_date]
    
    if to_date:
        if "trip_date" in filters:
            filters["trip_date"] = ["between", [from_date, to_date]]
        else:
            filters["trip_date"] = ["<=", to_date]
    
    if route:
        filters["route"] = route
    
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    
    # الحصول على الرحلات
    trips = frappe.get_all(
        "Trip",
        filters=filters,
        fields=["name", "trip_code", "route", "trip_date", "departure_time", 
                "arrival_time", "vehicle_type", "total_seats", "available_seats", 
                "price", "status"],
        order_by="trip_date, departure_time"
    )
    
    # الحصول على تفاصيل الرحلات
    trip_details = []
    
    for trip in trips:
        # الحصول على تفاصيل المسار
        route_doc = frappe.get_doc("Route", trip.route)
        from_city_name = frappe.get_value("City", route_doc.from_city, "city_name")
        to_city_name = frappe.get_value("City", route_doc.to_city, "city_name")
        
        # حساب عدد التذاكر المباعة
        sold_tickets = frappe.get_all(
            "Ticket",
            filters={"trip": trip.name, "status": ["!=", "ملغاة"]},
            fields=["name"]
        )
        
        sold_tickets_count = len(sold_tickets)
        occupancy_rate = (sold_tickets_count / trip.total_seats) * 100 if trip.total_seats > 0 else 0
        
        # حساب إجمالي المبيعات للرحلة
        tickets = frappe.get_all(
            "Ticket",
            filters={"trip": trip.name, "status": ["!=", "ملغاة"]},
            fields=["price"]
        )
        
        total_sales = sum(ticket.price for ticket in tickets)
        
        trip_details.append({
            "trip_code": trip.trip_code,
            "from_city": from_city_name,
            "to_city": to_city_name,
            "trip_date": trip.trip_date,
            "departure_time": trip.departure_time,
            "arrival_time": trip.arrival_time,
            "vehicle_type": trip.vehicle_type,
            "total_seats": trip.total_seats,
            "sold_tickets": sold_tickets_count,
            "available_seats": trip.available_seats,
            "occupancy_rate": occupancy_rate,
            "price": trip.price,
            "total_sales": total_sales,
            "status": trip.status
        })
    
    # حساب الإحصائيات
    total_trips = len(trip_details)
    total_seats = sum(trip["total_seats"] for trip in trip_details)
    total_sold_tickets = sum(trip["sold_tickets"] for trip in trip_details)
    total_sales = sum(trip["total_sales"] for trip in trip_details)
    
    avg_occupancy_rate = (total_sold_tickets / total_seats) * 100 if total_seats > 0 else 0
    
    # تصنيف الرحلات حسب المسار
    trips_by_route = {}
    for trip in trip_details:
        route_name = f"{trip['from_city']} - {trip['to_city']}"
        if route_name not in trips_by_route:
            trips_by_route[route_name] = {
                "count": 0,
                "sold_tickets": 0,
                "total_sales": 0
            }
        
        trips_by_route[route_name]["count"] += 1
        trips_by_route[route_name]["sold_tickets"] += trip["sold_tickets"]
        trips_by_route[route_name]["total_sales"] += trip["total_sales"]
    
    # تصنيف الرحلات حسب التاريخ
    trips_by_date = {}
    for trip in trip_details:
        trip_date = trip["trip_date"].strftime("%Y-%m-%d")
        if trip_date not in trips_by_date:
            trips_by_date[trip_date] = {
                "count": 0,
                "sold_tickets": 0,
                "total_sales": 0
            }
        
        trips_by_date[trip_date]["count"] += 1
        trips_by_date[trip_date]["sold_tickets"] += trip["sold_tickets"]
        trips_by_date[trip_date]["total_sales"] += trip["total_sales"]
    
    # تصنيف الرحلات حسب نوع المركبة
    trips_by_vehicle_type = {}
    for trip in trip_details:
        vehicle_type = trip["vehicle_type"]
        if vehicle_type not in trips_by_vehicle_type:
            trips_by_vehicle_type[vehicle_type] = {
                "count": 0,
                "sold_tickets": 0,
                "total_sales": 0
            }
        
        trips_by_vehicle_type[vehicle_type]["count"] += 1
        trips_by_vehicle_type[vehicle_type]["sold_tickets"] += trip["sold_tickets"]
        trips_by_vehicle_type[vehicle_type]["total_sales"] += trip["total_sales"]
    
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_trips": total_trips,
        "total_seats": total_seats,
        "total_sold_tickets": total_sold_tickets,
        "total_sales": total_sales,
        "avg_occupancy_rate": avg_occupancy_rate,
        "trips_by_route": trips_by_route,
        "trips_by_date": trips_by_date,
        "trips_by_vehicle_type": trips_by_vehicle_type,
        "details": trip_details
    }

def get_agents_performance_report(from_date=None, to_date=None):
    """
    الحصول على تقرير أداء الوكلاء
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        
    العائد:
        تقرير أداء الوكلاء مع إحصائيات وتفاصيل الأداء
    """
    # الحصول على جميع الوكلاء
    agents = frappe.get_all(
        "Agent",
        fields=["name", "agent_name", "agent_code", "agent_type", "commission_rate", "current_balance", "status"]
    )
    
    # تحديد فترة التقرير
    filters = {}
    
    if from_date:
        filters["booking_date"] = [">=", from_date]
    
    if to_date:
        if "booking_date" in filters:
            filters["booking_date"] = ["between", [from_date, to_date]]
        else:
            filters["booking_date"] = ["<=", to_date]
    
    # الحصول على تفاصيل أداء كل وكيل
    agent_performance = []
    
    for agent in agents:
        # الحصول على الحجوزات للوكيل
        agent_filters = filters.copy()
        agent_filters["agent"] = agent.name
        agent_filters["booking_status"] = ["!=", "ملغى"]
        
        bookings = frappe.get_all(
            "Booking",
            filters=agent_filters,
            fields=["name", "booking_number", "booking_date", "total_amount", "commission_amount"]
        )
        
        # الحصول على التذاكر المرتبطة بالحجوزات
        tickets_count = 0
        for booking in bookings:
            tickets = frappe.get_all(
                "Ticket",
                filters={"booking": booking.name, "status": ["!=", "ملغاة"]},
                fields=["name"]
            )
            tickets_count += len(tickets)
        
        # حساب الإحصائيات
        total_bookings = len(bookings)
        total_sales = sum(booking.total_amount for booking in bookings)
        total_commission = sum(booking.commission_amount or 0 for booking in bookings)
        
        # الحصول على المدفوعات للوكيل
        payment_filters = {}
        
        if from_date:
            payment_filters["payment_date"] = [">=", from_date]
        
        if to_date:
            if "payment_date" in payment_filters:
                payment_filters["payment_date"] = ["between", [from_date, to_date]]
            else:
                payment_filters["payment_date"] = ["<=", to_date]
        
        payment_filters["agent"] = agent.name
        payment_filters["docstatus"] = 1
        
        payments = frappe.get_all(
            "Agent Payment",
            filters=payment_filters,
            fields=["name", "payment_number", "payment_date", "amount", "payment_type"]
        )
        
        total_payments = sum(payment.amount for payment in payments)
        
        agent_performance.append({
            "agent_name": agent.agent_name,
            "agent_code": agent.agent_code,
            "agent_type": agent.agent_type,
            "commission_rate": agent.commission_rate,
            "current_balance": agent.current_balance,
            "status": agent.status,
            "total_bookings": total_bookings,
            "total_tickets": tickets_count,
            "total_sales": total_sales,
            "total_commission": total_commission,
            "total_payments": total_payments
        })
    
    # ترتيب الوكلاء حسب إجمالي المبيعات
    agent_performance.sort(key=lambda x: x["total_sales"], reverse=True)
    
    # حساب الإحصائيات الإجمالية
    total_agents = len(agent_performance)
    total_bookings = sum(agent["total_bookings"] for agent in agent_performance)
    total_tickets = sum(agent["total_tickets"] for agent in agent_performance)
    total_sales = sum(agent["total_sales"] for agent in agent_performance)
    total_commission = sum(agent["total_commission"] for agent in agent_performance)
    
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_agents": total_agents,
        "total_bookings": total_bookings,
        "total_tickets": total_tickets,
        "total_sales": total_sales,
        "total_commission": total_commission,
        "agent_performance": agent_performance
    }

def get_financial_report(from_date=None, to_date=None):
    """
    الحصول على التقرير المالي
    
    المعلمات:
        from_date: تاريخ البداية (اختياري)
        to_date: تاريخ النهاية (اختياري)
        
    العائد:
        التقرير المالي مع إحصائيات وتفاصيل المعاملات المالية
    """
    # تحديد فترة التقرير
    booking_filters = {}
    
    if from_date:
        booking_filters["booking_date"] = [">=", from_date]
    
    if to_date:
        if "booking_date" in booking_filters:
            booking_filters["booking_date"] = ["between", [from_date, to_date]]
        else:
            booking_filters["booking_date"] = ["<=", to_date]
    
    # الحصول على الحجوزات
    bookings = frappe.get_all(
        "Booking",
        filters=booking_filters,
        fields=["name", "booking_number", "booking_date", "customer", "agent", 
                "total_amount", "paid_amount", "booking_status", "payment_status"]
    )
    
    # الحصول على المدفوعات
    payment_filters = {}
    
    if from_date:
        payment_filters["payment_date"] = [">=", from_date]
    
    if to_date:
        if "payment_date" in payment_filters:
            payment_filters["payment_date"] = ["between", [from_date, to_date]]
        else:
            payment_filters["payment_date"] = ["<=", to_date]
    
    agent_payments = frappe.get_all(
        "Agent Payment",
        filters=payment_filters,
        fields=["name", "payment_number", "payment_date", "agent", "amount", "payment_type", "payment_method"]
    )
    
    # إنشاء قائمة بجميع المعاملات المالية
    transactions = []
    
    for booking in bookings:
        customer_name = frappe.get_value("Customer", booking.customer, "customer_name")
        agent_name = None
        if booking.agent:
            agent_name = frappe.get_value("Agent", booking.agent, "agent_name")
        
        transactions.append({
            "date": booking.booking_date,
            "type": "حجز",
            "reference": booking.booking_number,
            "description": f"حجز رقم {booking.booking_number}",
            "customer": customer_name,
            "agent": agent_name,
            "debit": 0,
            "credit": booking.total_amount,
            "paid_amount": booking.paid_amount,
            "status": booking.booking_status
        })
    
    for payment in agent_payments:
        agent_name = frappe.get_value("Agent", payment.agent, "agent_name")
        
        transactions.append({
            "date": payment.payment_date,
            "type": "دفعة وكيل",
            "reference": payment.payment_number,
            "description": f"دفعة وكيل رقم {payment.payment_number} ({payment.payment_type})",
            "customer": None,
            "agent": agent_name,
            "debit": payment.amount,
            "credit": 0,
            "paid_amount": payment.amount,
            "status": "مكتمل"
        })
    
    # ترتيب المعاملات حسب التاريخ
    transactions.sort(key=lambda x: x["date"])
    
    # حساب الإحصائيات المالية
    total_revenue = sum(transaction["credit"] for transaction in transactions)
    total_expenses = sum(transaction["debit"] for transaction in transactions)
    net_income = total_revenue - total_expenses
    
    total_received = sum(transaction["paid_amount"] for transaction in transactions if transaction["type"] == "حجز")
    total_receivable = sum(transaction["credit"] - transaction["paid_amount"] for transaction in transactions if transaction["type"] == "حجز")
    
    # تصنيف الإيرادات حسب التاريخ
    revenue_by_date = {}
    for transaction in transactions:
        if transaction["credit"] > 0:
            transaction_date = transaction["date"].strftime("%Y-%m-%d")
            if transaction_date not in revenue_by_date:
                revenue_by_date[transaction_date] = 0
            
            revenue_by_date[transaction_date] += transaction["credit"]
    
    # تصنيف الإيرادات حسب الوكيل
    revenue_by_agent = {}
    for transaction in transactions:
        if transaction["credit"] > 0 and transaction["agent"]:
            if transaction["agent"] not in revenue_by_agent:
                revenue_by_agent[transaction["agent"]] = 0
            
            revenue_by_agent[transaction["agent"]] += transaction["credit"]
    
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": net_income,
        "total_received": total_received,
        "total_receivable": total_receivable,
        "revenue_by_date": revenue_by_date,
        "revenue_by_agent": revenue_by_agent,
        "transactions": transactions
    }

def get_dashboard_data(period="today"):
    """
    الحصول على بيانات لوحة التحكم
    
    المعلمات:
        period: الفترة الزمنية (today, yesterday, this_week, this_month, last_month, this_year)
        
    العائد:
        بيانات لوحة التحكم مع إحصائيات وتفاصيل
    """
    # تحديد فترة التقرير
    today = datetime.date.today()
    from_date = None
    to_date = None
    
    if period == "today":
        from_date = today
        to_date = today
    elif period == "yesterday":
        from_date = today - datetime.timedelta(days=1)
        to_date = from_date
    elif period == "this_week":
        from_date = today - datetime.timedelta(days=today.weekday())
        to_date = today
    elif period == "this_month":
        from_date = today.replace(day=1)
        to_date = today
    elif period == "last_month":
        last_month = today.replace(day=1) - datetime.timedelta(days=1)
        from_date = last_month.replace(day=1)
        to_date = last_month.replace(day=calendar.monthrange(last_month.year, last_month.month)[1])
    elif period == "this_year":
        from_date = today.replace(month=1, day=1)
        to_date = today
    
    # الحصول على إحصائيات المبيعات
    sales_report = get_sales_report(from_date, to_date)
    
    # الحصول على إحصائيات الرحلات
    trips_report = get_trips_report(from_date, to_date)
    
    # الحصول على أداء الوكلاء
    agents_report = get_agents_performance_report(from_date, to_date)
    
    # الحصول على الرحلات القادمة
    upcoming_trips = frappe.get_all(
        "Trip",
        filters={"trip_date": [">=", today], "status": "مؤكدة"},
        fields=["name", "trip_code", "route", "trip_date", "departure_time", 
                "total_seats", "available_seats", "status"],
        order_by="trip_date, departure_time",
        limit=10
    )
    
    upcoming_trips_details = []
    for trip in upcoming_trips:
        route_doc = frappe.get_doc("Route", trip.route)
        from_city_name = frappe.get_value("City", route_doc.from_city, "city_name")
        to_city_name = frappe.get_value("City", route_doc.to_city, "city_name")
        
        upcoming_trips_details.append({
            "trip_code": trip.trip_code,
            "route_name": f"{from_city_name} - {to_city_name}",
            "trip_date": trip.trip_date,
            "departure_time": trip.departure_time,
            "total_seats": trip.total_seats,
            "available_seats": trip.available_seats,
            "status": trip.status
        })
    
    # الحصول على أحدث الحجوزات
    recent_bookings = frappe.get_all(
        "Booking",
        fields=["name", "booking_number", "booking_date", "customer", "total_amount", "booking_status"],
        order_by="booking_date desc",
        limit=10
    )
    
    recent_bookings_details = []
    for booking in recent_bookings:
        customer_name = frappe.get_value("Customer", booking.customer, "customer_name")
        
        # الحصول على الرحلة المرتبطة بالحجز
        tickets = frappe.get_all(
            "Ticket",
            filters={"booking": booking.name},
            fields=["trip"],
            limit=1
        )
        
        trip_code = ""
        if tickets:
            trip_code = frappe.get_value("Trip", tickets[0].trip, "trip_code")
        
        recent_bookings_details.append({
            "booking_number": booking.booking_number,
            "booking_date": booking.booking_date,
            "customer_name": customer_name,
            "trip_code": trip_code,
            "total_amount": booking.total_amount,
            "booking_status": booking.booking_status
        })
    
    # إعداد بيانات الرسوم البيانية
    sales_chart_data = prepare_sales_chart_data(from_date, to_date)
    top_routes_data = prepare_top_routes_chart_data(from_date, to_date)
    
    return {
        "period": period,
        "from_date": from_date,
        "to_date": to_date,
        "total_tickets": sales_report["total_tickets"],
        "total_sales": sales_report["total_sales"],
        "total_passengers": sales_report["total_tickets"],
        "total_trips": trips_report["total_trips"],
        "upcoming_trips": upcoming_trips_details,
        "recent_bookings": recent_bookings_details,
        "agent_performance": agents_report["agent_performance"],
        "sales_chart": sales_chart_data,
        "top_routes": top_routes_data
    }

def prepare_sales_chart_data(from_date, to_date):
    """
    إعداد بيانات الرسم البياني للمبيعات
    
    المعلمات:
        from_date: تاريخ البداية
        to_date: تاريخ النهاية
        
    العائد:
        بيانات الرسم البياني للمبيعات
    """
    # تحديد فترة التقرير
    if not from_date or not to_date:
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=30)
        to_date = today
    
    # إنشاء قائمة بجميع التواريخ في الفترة
    date_list = []
    current_date = from_date
    while current_date <= to_date:
        date_list.append(current_date)
        current_date += datetime.timedelta(days=1)
    
    # الحصول على المبيعات لكل تاريخ
    sales_by_date = {}
    for date in date_list:
        sales_by_date[date.strftime("%Y-%m-%d")] = 0
    
    # الحصول على الحجوزات في الفترة
    bookings = frappe.get_all(
        "Booking",
        filters={"booking_date": ["between", [from_date, to_date]]},
        fields=["booking_date", "total_amount"]
    )
    
    # تجميع المبيعات حسب التاريخ
    for booking in bookings:
        booking_date = booking.booking_date.strftime("%Y-%m-%d")
        if booking_date in sales_by_date:
            sales_by_date[booking_date] += booking.total_amount
    
    # إعداد بيانات الرسم البياني
    labels = [date.strftime("%Y-%m-%d") for date in date_list]
    values = [sales_by_date[date.strftime("%Y-%m-%d")] for date in date_list]
    
    return {
        "labels": labels,
        "values": values
    }

def prepare_top_routes_chart_data(from_date, to_date):
    """
    إعداد بيانات الرسم البياني للمسارات الأكثر طلباً
    
    المعلمات:
        from_date: تاريخ البداية
        to_date: تاريخ النهاية
        
    العائد:
        بيانات الرسم البياني للمسارات الأكثر طلباً
    """
    # تحديد فترة التقرير
    filters = {}
    
    if from_date:
        filters["booking_date"] = [">=", from_date]
    
    if to_date:
        if "booking_date" in filters:
            filters["booking_date"] = ["between", [from_date, to_date]]
        else:
            filters["booking_date"] = ["<=", to_date]
    
    # الحصول على التذاكر المباعة في الفترة
    tickets = frappe.get_all(
        "Ticket",
        filters={"status": ["!=", "ملغاة"]},
        fields=["name", "trip"]
    )
    
    # تجميع التذاكر حسب المسار
    route_counts = {}
    
    for ticket in tickets:
        trip = frappe.get_doc("Trip", ticket.trip)
        route = frappe.get_doc("Route", trip.route)
        
        from_city_name = frappe.get_value("City", route.from_city, "city_name")
        to_city_name = frappe.get_value("City", route.to_city, "city_name")
        
        route_name = f"{from_city_name} - {to_city_name}"
        
        if route_name not in route_counts:
            route_counts[route_name] = 0
        
        route_counts[route_name] += 1
    
    # ترتيب المسارات حسب عدد التذاكر
    sorted_routes = sorted(route_counts.items(), key=lambda x: x[1], reverse=True)
    
    # أخذ أعلى 5 مسارات
    top_routes = sorted_routes[:5]
    
    # إعداد بيانات الرسم البياني
    labels = [route[0] for route in top_routes]
    values = [route[1] for route in top_routes]
    
    return {
        "labels": labels,
        "values": values
    }

def export_report_to_csv(report_data, report_type):
    """
    تصدير التقرير إلى ملف CSV
    
    المعلمات:
        report_data: بيانات التقرير
        report_type: نوع التقرير (sales, trips, agents, financial)
        
    العائد:
        مسار ملف CSV
    """
    import csv
    import os
    
    # تحديد اسم الملف
    file_name = f"{report_type}_report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join("/tmp", file_name)
    
    # إنشاء ملف CSV
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        if report_type == "sales":
            # تصدير تقرير المبيعات
            fieldnames = ["booking_number", "booking_date", "customer_name", "agent_name", 
                         "ticket_number", "passenger_name", "trip_code", "trip_date", 
                         "from_city", "to_city", "seat_number", "price", "status"]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for detail in report_data["details"]:
                writer.writerow(detail)
        
        elif report_type == "trips":
            # تصدير تقرير الرحلات
            fieldnames = ["trip_code", "from_city", "to_city", "trip_date", "departure_time", 
                         "arrival_time", "vehicle_type", "total_seats", "sold_tickets", 
                         "available_seats", "occupancy_rate", "price", "total_sales", "status"]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for detail in report_data["details"]:
                writer.writerow(detail)
        
        elif report_type == "agents":
            # تصدير تقرير أداء الوكلاء
            fieldnames = ["agent_name", "agent_code", "agent_type", "commission_rate", 
                         "current_balance", "status", "total_bookings", "total_tickets", 
                         "total_sales", "total_commission", "total_payments"]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for agent in report_data["agent_performance"]:
                writer.writerow(agent)
        
        elif report_type == "financial":
            # تصدير التقرير المالي
            fieldnames = ["date", "type", "reference", "description", "customer", 
                         "agent", "debit", "credit", "paid_amount", "status"]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for transaction in report_data["transactions"]:
                writer.writerow(transaction)
    
    return file_path

def export_report_to_pdf(report_data, report_type):
    """
    تصدير التقرير إلى ملف PDF
    
    المعلمات:
        report_data: بيانات التقرير
        report_type: نوع التقرير (sales, trips, agents, financial)
        
    العائد:
        مسار ملف PDF
    """
    import os
    
    # تحديد اسم الملف
    file_name = f"{report_type}_report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    html_path = os.path.join("/tmp", f"{file_name}.html")
    pdf_path = os.path.join("/tmp", f"{file_name}.pdf")
    
    # إنشاء ملف HTML
    with open(html_path, "w", encoding="utf-8") as htmlfile:
        # إنشاء محتوى HTML بناءً على نوع التقرير
        if report_type == "sales":
            html_content = frappe.render_template(
                "ticket_system/templates/reports/sales_report.html",
                {"report": report_data}
            )
        elif report_type == "trips":
            html_content = frappe.render_template(
                "ticket_system/templates/reports/trips_report.html",
                {"report": report_data}
            )
        elif report_type == "agents":
            html_content = frappe.render_template(
                "ticket_system/templates/reports/agents_report.html",
                {"report": report_data}
            )
        elif report_type == "financial":
            html_content = frappe.render_template(
                "ticket_system/templates/reports/financial_report.html",
                {"report": report_data}
            )
        
        htmlfile.write(html_content)
    
    # تحويل HTML إلى PDF
    os.system(f"wkhtmltopdf {html_path} {pdf_path}")
    
    return pdf_path
