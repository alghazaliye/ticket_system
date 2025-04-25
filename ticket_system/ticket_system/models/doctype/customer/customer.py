import frappe
from frappe.model.document import Document
import random
import string

class Customer(Document):
    def before_save(self):
        # Auto-generate customer ID if not provided
        if not self.customer_id or self.customer_id == "New Customer":
            self.customer_id = self.generate_customer_id()
            
        # Set full name from first and last name
        self.full_name = f"{self.first_name} {self.last_name}"
    
    def validate(self):
        # Validate phone number format
        if self.phone and not self.is_valid_phone_number(self.phone):
            frappe.throw("رقم الهاتف غير صالح")
            
        # Validate email format if provided
        if self.email and not self.is_valid_email(self.email):
            frappe.throw("البريد الإلكتروني غير صالح")
    
    def generate_customer_id(self):
        # Generate a unique customer ID
        prefix = "CUST"
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_part}"
    
    def is_valid_phone_number(self, phone):
        # Basic phone validation - can be enhanced based on specific requirements
        # Remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")
        # Check if it's numeric and has reasonable length
        return phone.isdigit() and 7 <= len(phone) <= 15
    
    def is_valid_email(self, email):
        # Basic email validation
        return "@" in email and "." in email.split("@")[1]
    
    def add_loyalty_points(self, points):
        """
        Add loyalty points to customer
        
        Args:
            points: Number of points to add
        """
        if points > 0:
            self.loyalty_points += points
            self.save()
            
            # Log the transaction
            frappe.logger().info(
                f"Added {points} loyalty points to customer {self.full_name} ({self.customer_id}). "
                f"New balance: {self.loyalty_points}"
            )
