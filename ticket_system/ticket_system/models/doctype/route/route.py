# -*- coding: utf-8 -*-
# Copyright (c) 2025, المنتصر للنقل الدولي and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Route(Document):
    """
    Route DocType for storing route information between cities.
    
    Fields:
    - from_city: Source city
    - to_city: Destination city
    - distance: Distance between cities in kilometers
    - estimated_time: Estimated travel time in hours
    - is_active: Whether the route is active for booking
    - route_code: Unique code for the route
    """
    
    def validate(self):
        """Validate route data before saving."""
        self.validate_cities()
        self.validate_route_code()
        self.validate_distance_and_time()
    
    def validate_cities(self):
        """Ensure from_city and to_city are different."""
        if self.from_city == self.to_city:
            frappe.throw("المدينة المصدر والوجهة يجب أن تكونا مختلفتين")
        
        # Check if cities exist and are active
        for city_field in ['from_city', 'to_city']:
            city = self.get(city_field)
            if city:
                city_doc = frappe.get_doc("City", city)
                if not city_doc.is_active:
                    frappe.throw(f"المدينة {city} غير نشطة")
    
    def validate_route_code(self):
        """Ensure route code is unique and properly formatted."""
        if not self.route_code:
            # Auto-generate route code if not provided
            self.route_code = self.generate_route_code()
        else:
            # Ensure route code is uppercase
            self.route_code = self.route_code.upper()
            
            # Check if route code already exists (excluding this document)
            existing = frappe.db.get_all(
                "Route", 
                filters={"route_code": self.route_code, "name": ["!=", self.name]},
                limit=1
            )
            
            if existing:
                frappe.throw(f"رمز المسار {self.route_code} موجود بالفعل. الرجاء استخدام رمز مختلف.")
    
    def validate_distance_and_time(self):
        """Validate distance and estimated time values."""
        if self.distance and self.distance <= 0:
            frappe.throw("يجب أن تكون المسافة أكبر من صفر")
        
        if self.estimated_time and self.estimated_time <= 0:
            frappe.throw("يجب أن يكون الوقت المقدر أكبر من صفر")
    
    def generate_route_code(self):
        """Generate a unique route code based on cities."""
        from_city_doc = frappe.get_doc("City", self.from_city)
        to_city_doc = frappe.get_doc("City", self.to_city)
        
        # Create code using city codes
        code_base = f"{from_city_doc.city_code}-{to_city_doc.city_code}"
        
        # Check if this code already exists
        existing = frappe.db.get_all(
            "Route", 
            filters={"route_code": code_base},
            limit=1
        )
        
        if not existing:
            return code_base
        
        # If code exists, append a number
        i = 1
        while True:
            new_code = f"{code_base}-{i}"
            existing = frappe.db.get_all(
                "Route", 
                filters={"route_code": new_code},
                limit=1
            )
            
            if not existing:
                return new_code
            
            i += 1
