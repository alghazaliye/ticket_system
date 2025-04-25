import frappe
from frappe.model.document import Document
import random
import string

class Payment(Document):
    def before_save(self):
        # Auto-generate payment number if not provided
        if not self.payment_number or self.payment_number == "New Payment":
            self.payment_number = self.generate_payment_number()
            
        # Set received_by to current user if not specified
        if not self.received_by:
            self.received_by = frappe.session.user
    
    def validate(self):
        # Validate amount is positive
        if self.amount <= 0:
            frappe.throw("مبلغ الدفع يجب أن يكون أكبر من صفر")
            
        # Validate booking exists and is not cancelled
        booking = frappe.get_doc("Booking", self.booking)
        if booking.booking_status == "ملغى":
            frappe.throw("لا يمكن إضافة دفعة لحجز ملغى")
            
        # Validate amount does not exceed remaining balance
        if self.amount > (booking.total_amount - booking.paid_amount):
            frappe.throw("مبلغ الدفع يتجاوز الرصيد المتبقي للحجز")
    
    def on_submit(self):
        # Update booking paid amount and payment status
        self.update_booking_payment()
    
    def on_cancel(self):
        # Reverse booking paid amount and payment status
        self.reverse_booking_payment()
    
    def generate_payment_number(self):
        # Generate a unique payment number
        prefix = "PAY"
        random_part = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{random_part}"
    
    def update_booking_payment(self):
        # Update booking paid amount and payment status
        booking = frappe.get_doc("Booking", self.booking)
        booking.paid_amount += self.amount
        
        # Update payment status
        if booking.paid_amount <= 0:
            booking.payment_status = "غير مدفوع"
        elif booking.paid_amount < booking.total_amount:
            booking.payment_status = "مدفوع جزئياً"
        else:
            booking.payment_status = "مدفوع بالكامل"
            
        # Update booking status to confirmed if fully paid
        if booking.payment_status == "مدفوع بالكامل" and booking.booking_status == "مؤقت":
            booking.booking_status = "مؤكد"
            
        booking.save()
        
        # Log the payment
        frappe.logger().info(
            f"Payment {self.payment_number} for booking {booking.booking_number}: "
            f"Amount: {self.amount}, Method: {self.payment_method}, "
            f"New Paid Amount: {booking.paid_amount}, Status: {booking.payment_status}"
        )
    
    def reverse_booking_payment(self):
        # Reverse booking paid amount and payment status
        booking = frappe.get_doc("Booking", self.booking)
        booking.paid_amount -= self.amount
        
        # Update payment status
        if booking.paid_amount <= 0:
            booking.payment_status = "غير مدفوع"
        elif booking.paid_amount < booking.total_amount:
            booking.payment_status = "مدفوع جزئياً"
        else:
            booking.payment_status = "مدفوع بالكامل"
            
        # Update booking status to temporary if not fully paid
        if booking.payment_status != "مدفوع بالكامل" and booking.booking_status == "مؤكد":
            booking.booking_status = "مؤقت"
            
        booking.save()
        
        # Log the payment reversal
        frappe.logger().info(
            f"Payment {self.payment_number} reversed for booking {booking.booking_number}: "
            f"Amount: {self.amount}, Method: {self.payment_method}, "
            f"New Paid Amount: {booking.paid_amount}, Status: {booking.payment_status}"
        )
