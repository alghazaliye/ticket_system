import frappe
from frappe.model.document import Document

class Vehicle(Document):
    def validate(self):
        # Validate capacity is positive
        if self.capacity <= 0:
            frappe.throw("سعة المركبة يجب أن تكون أكبر من صفر")
            
        # Validate year is reasonable
        current_year = frappe.utils.today().year
        if self.year < 1950 or self.year > current_year + 1:
            frappe.throw(f"سنة الصنع يجب أن تكون بين 1950 و {current_year + 1}")
            
        # Validate maintenance dates
        if self.last_maintenance_date and self.next_maintenance_date:
            if self.next_maintenance_date < self.last_maintenance_date:
                frappe.throw("تاريخ الصيانة القادمة يجب أن يكون بعد تاريخ آخر صيانة")
                
    def before_save(self):
        # Set next maintenance date if not specified
        if self.last_maintenance_date and not self.next_maintenance_date:
            # Default to 3 months after last maintenance
            self.next_maintenance_date = frappe.utils.add_months(self.last_maintenance_date, 3)
            
    def schedule_maintenance(self, maintenance_date, notes=None):
        """
        Schedule maintenance for the vehicle
        
        Args:
            maintenance_date: Date of scheduled maintenance
            notes: Maintenance notes
        """
        # Update vehicle status and maintenance info
        self.status = "في الصيانة"
        self.next_maintenance_date = maintenance_date
        
        if notes:
            self.maintenance_notes = notes
            
        self.save()
        
        # Log the maintenance schedule
        frappe.logger().info(
            f"Maintenance scheduled for vehicle {self.vehicle_number}: "
            f"Date: {maintenance_date}, Notes: {notes or 'None'}"
        )
        
    def complete_maintenance(self, completion_date=None, notes=None):
        """
        Complete maintenance for the vehicle
        
        Args:
            completion_date: Date of maintenance completion
            notes: Maintenance notes
        """
        # Update vehicle status and maintenance info
        self.status = "متاحة"
        self.last_maintenance_date = completion_date or frappe.utils.today()
        self.next_maintenance_date = frappe.utils.add_months(self.last_maintenance_date, 3)
        
        if notes:
            self.maintenance_notes = notes
            
        self.save()
        
        # Log the maintenance completion
        frappe.logger().info(
            f"Maintenance completed for vehicle {self.vehicle_number}: "
            f"Date: {self.last_maintenance_date}, Next: {self.next_maintenance_date}, "
            f"Notes: {notes or 'None'}"
        )
