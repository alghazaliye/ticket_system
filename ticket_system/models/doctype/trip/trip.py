# -*- coding: utf-8 -*-
# Copyright (c) 2025, المنتصر للنقل الدولي and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class Trip(Document):
    """
    Trip DocType for storing trip information.
    
    Fields:
    - route: Link to Route doctype
    - trip_date: Date of the trip
    - departure_time: Departure time
    - arrival_time: Arrival time
    - vehicle_type: Type of vehicle (VIP, Regular, etc.)
    - total_seats: Total number of seats
    - available_seats: Number of available seats
    - price: Price per seat
    - currency: Currency for price
    - status: Status of the trip (Scheduled, In Progress, Completed, Cancelled)
    """
    
    def validate(self):
        """Validate trip data before saving."""
        self.validate_dates_and_times()
        self.validate_seats()
        self.validate_price()
        self.update_available_seats()
        self.set_trip_code()
    
    def validate_dates_and_times(self):
        """Validate trip dates and times."""
        # Ensure trip date is not in the past
        if self.trip_date and self.trip_date < datetime.now().date():
            if not self.is_new():  # Allow editing past trips for existing records
                pass
            else:
                frappe.throw("لا يمكن جدولة رحلة في تاريخ سابق")
        
        # Ensure arrival time is after departure time
        if self.departure_time and self.arrival_time:
            dep_time = datetime.strptime(self.departure_time, "%H:%M:%S")
            arr_time = datetime.strptime(self.arrival_time, "%H:%M:%S")
            
            if arr_time <= dep_time:
                frappe.throw("يجب أن يكون وقت الوصول بعد وقت المغادرة")
    
    def validate_seats(self):
        """Validate seat information."""
        if self.total_seats <= 0:
            frappe.throw("يجب أن يكون عدد المقاعد الكلي أكبر من صفر")
        
        if self.is_new():
            self.available_seats = self.total_seats
        elif self.available_seats > self.total_seats:
            self.available_seats = self.total_seats
    
    def validate_price(self):
        """Validate price information."""
        if self.price <= 0:
            frappe.throw("يجب أن يكون السعر أكبر من صفر")
    
    def update_available_seats(self):
        """Update available seats based on bookings."""
        if not self.is_new():
            # Count booked seats from tickets
            booked_seats = frappe.db.count("Ticket", {"trip": self.name, "status": ["not in", ["Cancelled", "Refunded"]]})
            
            # Update available seats
            self.available_seats = max(0, self.total_seats - booked_seats)
    
    def set_trip_code(self):
        """Set trip code if not already set."""
        if not self.trip_code:
            route = frappe.get_doc("Route", self.route)
            date_str = self.trip_date.strftime("%Y%m%d")
            time_str = self.departure_time.replace(":", "")[:4]
            
            self.trip_code = f"{route.route_code}-{date_str}-{time_str}"
            
            # Check if this code already exists
            existing = frappe.db.get_all(
                "Trip", 
                filters={"trip_code": self.trip_code, "name": ["!=", self.name]},
                limit=1
            )
            
            if existing:
                # Append a suffix to make it unique
                trips_on_same_route = frappe.db.count(
                    "Trip", 
                    filters={"route": self.route, "trip_date": self.trip_date}
                )
                self.trip_code = f"{self.trip_code}-{trips_on_same_route + 1}"
    
    def on_update(self):
        """Actions to perform when trip is updated."""
        self.update_tickets()
    
    def update_tickets(self):
        """Update tickets if trip details change."""
        if self.has_value_changed("status") and self.status in ["Cancelled", "Rescheduled"]:
            # Update all tickets for this trip
            tickets = frappe.get_all("Ticket", filters={"trip": self.name, "status": "Confirmed"})
            
            for ticket in tickets:
                ticket_doc = frappe.get_doc("Ticket", ticket.name)
                
                if self.status == "Cancelled":
                    ticket_doc.status = "Cancelled"
                    ticket_doc.add_comment("Comment", "تم إلغاء التذكرة بسبب إلغاء الرحلة")
                elif self.status == "Rescheduled":
                    ticket_doc.status = "Rescheduled"
                    ticket_doc.add_comment("Comment", "تم إعادة جدولة التذكرة بسبب إعادة جدولة الرحلة")
                
                ticket_doc.save(ignore_permissions=True)
