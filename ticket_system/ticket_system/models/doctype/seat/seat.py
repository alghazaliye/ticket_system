import frappe
from frappe.model.document import Document

class Seat(Document):
    def before_save(self):
        # Auto-generate seat_id if not provided
        if not self.seat_id or self.seat_id == "New Seat":
            self.seat_id = self.generate_seat_id()
    
    def validate(self):
        # Validate seat number is positive
        if self.seat_number <= 0:
            frappe.throw("رقم المقعد يجب أن يكون أكبر من صفر")
            
        # Validate price factor is positive
        if self.price_factor <= 0:
            frappe.throw("عامل السعر يجب أن يكون أكبر من صفر")
            
        # Validate seat number is unique for this vehicle
        self.validate_unique_seat_number()
    
    def generate_seat_id(self):
        # Generate a unique seat ID based on vehicle and seat number
        vehicle_doc = frappe.get_doc("Vehicle", self.vehicle)
        vehicle_code = vehicle_doc.vehicle_number[:3].upper()
        return f"{vehicle_code}-{self.seat_number:03d}"
    
    def validate_unique_seat_number(self):
        # Check if seat number already exists for this vehicle
        existing_seats = frappe.get_all(
            "Seat",
            filters={
                "vehicle": self.vehicle,
                "seat_number": self.seat_number,
                "name": ["!=", self.name]
            }
        )
        
        if existing_seats:
            frappe.throw(f"رقم المقعد {self.seat_number} موجود بالفعل في هذه المركبة")
    
    def calculate_price(self, base_price):
        """
        Calculate the price for this seat based on base price and price factor
        
        Args:
            base_price: Base price for the trip
            
        Returns:
            float: Calculated price for this seat
        """
        return base_price * self.price_factor
