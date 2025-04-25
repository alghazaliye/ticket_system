import frappe
from frappe.model.document import Document

class Agent(Document):
    def before_save(self):
        # Validate commission rate is within acceptable range
        if self.commission_rate < 0 or self.commission_rate > 100:
            frappe.throw("نسبة العمولة يجب أن تكون بين 0 و 100")
            
        # If agent type is individual, clear contact person
        if self.agent_type == "فردي" and self.contact_person:
            self.contact_person = ""
            
    def validate(self):
        # Ensure credit limit is not negative
        if self.credit_limit < 0:
            frappe.throw("حد الائتمان لا يمكن أن يكون سالباً")
            
    def update_balance(self, amount, transaction_type="sale"):
        """
        Update agent balance
        
        Args:
            amount: Amount to add/subtract from balance
            transaction_type: Type of transaction (sale, payment, refund)
        """
        if transaction_type == "sale":
            # For sales, increase the balance (agent owes more)
            self.current_balance += amount
        elif transaction_type == "payment":
            # For payments, decrease the balance (agent paid)
            self.current_balance -= amount
        elif transaction_type == "refund":
            # For refunds, decrease the balance (company owes agent)
            self.current_balance -= amount
            
        self.save()
        
        # Log the transaction
        self.log_transaction(amount, transaction_type)
        
    def log_transaction(self, amount, transaction_type):
        """
        Log agent transaction for reporting and auditing
        """
        # This would create a record in a transaction log doctype
        # For now, we'll just log it
        frappe.logger().info(
            f"Agent transaction: {self.agent_name} ({self.agent_code}), "
            f"Type: {transaction_type}, Amount: {amount}, "
            f"New Balance: {self.current_balance}"
        )
