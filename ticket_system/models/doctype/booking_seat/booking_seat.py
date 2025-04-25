import frappe
from frappe.model.document import Document

class BookingSeat(Document):
    def validate(self):
        # Validate seat number is positive
        if self.seat_number <= 0:
            frappe.throw("رقم المقعد يجب أن يكون أكبر من صفر")
            
        # Validate price is positive
        if self.price <= 0:
            frappe.throw("سعر المقعد يجب أن يكون أكبر من صفر")
