import frappe
from frappe.model.document import Document

class City(Document):
    """
    City DocType for storing city information.
    
    Fields:
    - city_name: Name of the city
    - city_code: Unique code for the city
    - country: Country where the city is located
    - is_active: Whether the city is active for booking
    """
    
    def validate(self):
        """Validate city data before saving."""
        self.validate_city_code()
    
    def validate_city_code(self):
        """Ensure city code is unique and properly formatted."""
        if not self.city_code:
            # Auto-generate city code if not provided
            self.city_code = self.generate_city_code()
        else:
            # Ensure city code is uppercase
            self.city_code = self.city_code.upper()
            
            # Check if city code already exists (excluding this document)
            existing = frappe.db.get_all(
                "City", 
                filters={"city_code": self.city_code, "name": ["!=", self.name]},
                limit=1
            )
            
            if existing:
                frappe.throw(f"City code {self.city_code} already exists. Please use a different code.")
    
    def generate_city_code(self):
        """Generate a unique city code based on city name."""
        # Take first 3 letters of city name and convert to uppercase
        code_base = self.city_name[:3].upper()
        
        # Check if this code already exists
        existing = frappe.db.get_all(
            "City", 
            filters={"city_code": code_base},
            limit=1
        )
        
        if not existing:
            return code_base
        
        # If code exists, append a number
        i = 1
        while True:
            new_code = f"{code_base}{i}"
            existing = frappe.db.get_all(
                "City", 
                filters={"city_code": new_code},
                limit=1
            )
            
            if not existing:
                return new_code
            
            i += 1
