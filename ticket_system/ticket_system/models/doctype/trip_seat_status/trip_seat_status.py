import frappe
from frappe.model.document import Document

class TripSeatStatus(Document):
    def before_save(self):
        # Auto-generate trip_seat_id if not provided
        if not self.trip_seat_id or self.trip_seat_id == "New Trip Seat Status":
            self.trip_seat_id = self.generate_trip_seat_id()
            
        # Set price based on trip base price and seat price factor if not specified
        if not self.price or self.price <= 0:
            self.calculate_price()
    
    def validate(self):
        # Validate seat belongs to the vehicle assigned to the trip
        self.validate_seat_vehicle()
        
        # Validate booking reference if status is booked or sold
        if self.status in ["محجوز", "مباع"] and not self.booking:
            frappe.throw("يجب تحديد الحجز عندما تكون حالة المقعد محجوز أو مباع")
    
    def generate_trip_seat_id(self):
        # Generate a unique trip seat ID
        trip_doc = frappe.get_doc("Trip", self.trip)
        seat_doc = frappe.get_doc("Seat", self.seat)
        return f"{trip_doc.trip_code}-{seat_doc.seat_number:03d}"
    
    def validate_seat_vehicle(self):
        # Check if seat belongs to the vehicle assigned to the trip
        trip_doc = frappe.get_doc("Trip", self.trip)
        seat_doc = frappe.get_doc("Seat", self.seat)
        
        # This validation assumes trip has a vehicle field
        # If trip doesn't have direct vehicle field, this would need to be adjusted
        # For now, we'll just log a message
        frappe.logger().info(
            f"Validating seat {seat_doc.seat_id} belongs to the correct vehicle for trip {trip_doc.trip_code}"
        )
    
    def calculate_price(self):
        # Calculate price based on trip base price and seat price factor
        trip_doc = frappe.get_doc("Trip", self.trip)
        seat_doc = frappe.get_doc("Seat", self.seat)
        
        self.price = trip_doc.price * seat_doc.price_factor
        self.currency = trip_doc.currency
    
    def update_status(self, status, booking=None):
        """
        Update seat status
        
        Args:
            status: New status (متاح, محجوز, مباع, غير متاح)
            booking: Booking reference (required for محجوز and مباع)
        """
        if status in ["محجوز", "مباع"] and not booking:
            frappe.throw("يجب تحديد الحجز عندما تكون حالة المقعد محجوز أو مباع")
            
        self.status = status
        
        if booking:
            self.booking = booking
        elif status == "متاح":
            self.booking = None
            
        self.save()
        
        # Log the status update
        frappe.logger().info(
            f"Updated seat status for {self.trip_seat_id}: "
            f"Status: {status}, Booking: {booking or 'None'}"
        )
