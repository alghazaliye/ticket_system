import frappe
from frappe import _

def search_trips(source_city=None, destination_city=None, trip_date=None, vehicle_type=None, min_price=None, max_price=None):
    """
    البحث عن الرحلات المتاحة بناءً على معايير البحث
    
    المعلمات:
        source_city: مدينة المصدر
        destination_city: مدينة الوجهة
        trip_date: تاريخ الرحلة
        vehicle_type: نوع المركبة
        min_price: الحد الأدنى للسعر
        max_price: الحد الأقصى للسعر
        
    العائد:
        قائمة بالرحلات المتاحة التي تطابق معايير البحث
    """
    filters = {}
    
    # إضافة الفلاتر إذا تم تحديدها
    if source_city:
        # البحث عن المسارات التي تبدأ من المدينة المحددة
        routes = frappe.get_all("Route", filters={"from_city": source_city}, fields=["name"])
        route_names = [r.name for r in routes]
        if route_names:
            filters["route"] = ["in", route_names]
        else:
            # إذا لم يتم العثور على مسارات، إرجاع قائمة فارغة
            return []
    
    if destination_city:
        # البحث عن المسارات التي تنتهي في المدينة المحددة
        routes = frappe.get_all("Route", filters={"to_city": destination_city}, fields=["name"])
        route_names = [r.name for r in routes]
        if route_names:
            if "route" in filters:
                # تقاطع مع المسارات المحددة سابقاً
                existing_routes = filters["route"][1]
                common_routes = [r for r in route_names if r in existing_routes]
                if common_routes:
                    filters["route"] = ["in", common_routes]
                else:
                    # إذا لم يتم العثور على مسارات مشتركة، إرجاع قائمة فارغة
                    return []
            else:
                filters["route"] = ["in", route_names]
        else:
            # إذا لم يتم العثور على مسارات، إرجاع قائمة فارغة
            return []
    
    if trip_date:
        filters["trip_date"] = trip_date
    
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    
    # إضافة فلاتر السعر
    if min_price is not None:
        filters["price"] = [">=", min_price]
    
    if max_price is not None:
        if "price" in filters:
            filters["price"] = ["between", [min_price, max_price]]
        else:
            filters["price"] = ["<=", max_price]
    
    # البحث عن الرحلات المجدولة فقط
    filters["status"] = ["in", ["مجدولة", "قيد التنفيذ"]]
    
    # الحصول على الرحلات التي تطابق الفلاتر
    trips = frappe.get_all(
        "Trip",
        filters=filters,
        fields=[
            "name", "trip_code", "route", "trip_date", "departure_time", 
            "arrival_time", "vehicle_type", "total_seats", "available_seats", 
            "price", "currency", "status"
        ]
    )
    
    # إضافة معلومات المسار لكل رحلة
    for trip in trips:
        route = frappe.get_doc("Route", trip.route)
        trip.from_city = route.from_city
        trip.to_city = route.to_city
        trip.distance = route.distance
        trip.estimated_time = route.estimated_time
    
    return trips

def get_available_seats(trip):
    """
    الحصول على المقاعد المتاحة للرحلة
    
    المعلمات:
        trip: معرف الرحلة
        
    العائد:
        قائمة بالمقاعد المتاحة للرحلة
    """
    # الحصول على حالة المقاعد للرحلة
    available_seats = frappe.get_all(
        "Trip Seat Status",
        filters={"trip": trip, "status": "متاح"},
        fields=["name", "seat", "price", "currency"]
    )
    
    # إضافة معلومات المقعد لكل حالة مقعد
    for seat_status in available_seats:
        seat = frappe.get_doc("Seat", seat_status.seat)
        seat_status.seat_number = seat.seat_number
        seat_status.seat_type = seat.seat_type
        seat_status.seat_position = seat.seat_position
    
    return available_seats

def get_trip_details(trip):
    """
    الحصول على تفاصيل الرحلة
    
    المعلمات:
        trip: معرف الرحلة
        
    العائد:
        تفاصيل الرحلة مع معلومات المسار والمقاعد المتاحة
    """
    # الحصول على معلومات الرحلة
    trip_doc = frappe.get_doc("Trip", trip)
    
    # الحصول على معلومات المسار
    route = frappe.get_doc("Route", trip_doc.route)
    
    # الحصول على المقاعد المتاحة
    available_seats = get_available_seats(trip)
    
    # إنشاء قاموس بتفاصيل الرحلة
    trip_details = {
        "trip": trip_doc,
        "route": route,
        "available_seats": available_seats,
        "from_city_name": frappe.get_value("City", route.from_city, "city_name"),
        "to_city_name": frappe.get_value("City", route.to_city, "city_name")
    }
    
    return trip_details
