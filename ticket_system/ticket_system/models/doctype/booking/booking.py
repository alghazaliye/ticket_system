import frappe
from frappe.model.document import Document
import random
import string

class Booking(Document):
    def before_save(self):
        # Auto-generate booking number if not provided
        if not self.booking_number or self.booking_number == "New Booking":
            self.booking_number = self.generate_booking_number()
            
        # Calculate total amount
        self.calculate_total_amount()
        
        # Calculate balance
        self.balance = self.total_amount - self.paid_amount
        
        # Set payment status based on paid amount
        self.set_payment_status()
        
        # Calculate commission if agent is specified
        if self.agent:
            self.calculate_commission()
    
    def validate(self):
        # Ensure trip has available seats
        self.validate_seat_availability()
        
        # Ensure paid amount is not greater than total amount
        if self.paid_amount > self.total_amount:
            frappe.throw("المبلغ المدفوع لا يمكن أن يكون أكبر من المبلغ الإجمالي")
    
    def on_submit(self):
        # Update seat status in trip
        self.update_seat_status("محجوز")
        
        # Create tickets for confirmed bookings
        if self.booking_status == "مؤكد":
            self.create_tickets()
            
        # Update agent balance if applicable
        if self.agent:
            self.update_agent_balance()
    
    def on_cancel(self):
        # Update seat status in trip
        self.update_seat_status("متاح")
        
        # Cancel associated tickets
        self.cancel_tickets()
        
        # Reverse agent balance update if applicable
        if self.agent:
            self.reverse_agent_balance()
    
    def generate_booking_number(self):
        # Generate a unique booking number
        prefix = "BK"
        random_part = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{random_part}"
    
    def calculate_total_amount(self):
        # Calculate total amount based on seats
        total = 0
        for seat in self.seats:
            total += seat.price
        self.total_amount = total
    
    def set_payment_status(self):
        # Set payment status based on paid amount
        if self.paid_amount <= 0:
            self.payment_status = "غير مدفوع"
        elif self.paid_amount < self.total_amount:
            self.payment_status = "مدفوع جزئياً"
        else:
            self.payment_status = "مدفوع بالكامل"
    
    def calculate_commission(self):
        # Get commission rate from agent if not specified
        if not self.commission_rate:
            agent_doc = frappe.get_doc("Agent", self.agent)
            self.commission_rate = agent_doc.commission_rate
        
        # Calculate commission amount
        self.commission_amount = (self.commission_rate / 100) * self.total_amount
    
    def validate_seat_availability(self):
        # Check if seats are available in the trip
        trip_doc = frappe.get_doc("Trip", self.trip)
        
        # Ensure trip has enough available seats
        if len(self.seats) > trip_doc.available_seats:
            frappe.throw(f"لا توجد مقاعد كافية متاحة في هذه الرحلة. المقاعد المتاحة: {trip_doc.available_seats}")
        
        # Validate each seat is available
        # This would require a more complex implementation in a real system
        # For now, we'll just log a message
        frappe.logger().info(f"Validating seat availability for booking {self.booking_number}")
    
    def update_seat_status(self, status):
        # Update seat status in trip
        # This would require a more complex implementation in a real system
        # For now, we'll just log a message
        frappe.logger().info(f"Updating seat status to {status} for booking {self.booking_number}")
        
        # Update available seats count in trip
        trip_doc = frappe.get_doc("Trip", self.trip)
        if status == "محجوز":
            trip_doc.available_seats -= len(self.seats)
        elif status == "متاح":
            trip_doc.available_seats += len(self.seats)
        trip_doc.save()
    
    def create_tickets(self):
        # Create tickets for each seat in the booking
        for seat in self.seats:
            ticket = frappe.new_doc("Ticket")
            ticket.trip = self.trip
            ticket.seat_number = seat.seat_number
            ticket.passenger_name = seat.passenger_name
            ticket.passenger_id_type = seat.passenger_id_type
            ticket.passenger_id_number = seat.passenger_id_number
            ticket.booking_date = self.booking_date
            ticket.issue_date = frappe.utils.now()
            ticket.price = seat.price
            ticket.currency = self.currency
            ticket.agent = self.agent
            ticket.status = "صالحة"
            ticket.insert()
    
    def cancel_tickets(self):
        # Cancel all tickets associated with this booking
        tickets = frappe.get_all("Ticket", filters={"booking_number": self.booking_number})
        for ticket_name in tickets:
            ticket = frappe.get_doc("Ticket", ticket_name.name)
            ticket.status = "ملغاة"
            ticket.save()
    
    def update_agent_balance(self):
        # Update agent balance
        if self.agent and self.commission_amount:
            agent_doc = frappe.get_doc("Agent", self.agent)
            agent_doc.update_balance(self.total_amount, "sale")
    
    def reverse_agent_balance(self):
        # Reverse agent balance update
        if self.agent and self.commission_amount:
            agent_doc = frappe.get_doc("Agent", self.agent)
            agent_doc.update_balance(self.total_amount, "refund")
