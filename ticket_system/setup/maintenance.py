import frappe
from frappe import _

def execute():
    """
    تنفيذ عمليات الصيانة الدورية
    """
    # تنظيف البيانات القديمة
    cleanup_old_data()
    
    # إعادة حساب الإحصائيات
    recalculate_statistics()
    
    # تحديث حالة الرحلات
    update_trip_status()
    
    frappe.db.commit()
    
    frappe.msgprint(_("تم تنفيذ عمليات الصيانة الدورية بنجاح"))

def cleanup_old_data():
    """
    تنظيف البيانات القديمة
    """
    # حذف سجلات التتبع القديمة
    frappe.db.sql("""
        DELETE FROM `tabTicket System Log`
        WHERE `creation` < DATE_SUB(NOW(), INTERVAL 3 MONTH)
    """)

def recalculate_statistics():
    """
    إعادة حساب الإحصائيات
    """
    # إعادة حساب إحصائيات الوكلاء
    agents = frappe.get_all("Agent", fields=["name"])
    for agent in agents:
        # حساب إجمالي المبيعات
        total_sales = frappe.db.sql("""
            SELECT SUM(b.total_amount) 
            FROM `tabBooking` b
            WHERE b.agent = %s AND b.booking_status != 'ملغى'
        """, agent.name)[0][0] or 0
        
        # حساب إجمالي العمولات
        total_commission = frappe.db.sql("""
            SELECT SUM(b.commission_amount) 
            FROM `tabBooking` b
            WHERE b.agent = %s AND b.booking_status != 'ملغى'
        """, agent.name)[0][0] or 0
        
        # تحديث إحصائيات الوكيل
        frappe.db.sql("""
            UPDATE `tabAgent` 
            SET `total_sales` = %s, `total_commission` = %s
            WHERE `name` = %s
        """, (total_sales, total_commission, agent.name))

def update_trip_status():
    """
    تحديث حالة الرحلات
    """
    # تحديث الرحلات المنتهية
    frappe.db.sql("""
        UPDATE `tabTrip`
        SET `status` = 'منتهية'
        WHERE `trip_date` < CURDATE() AND `status` = 'مؤكدة'
    """)
    
    # تحديث الرحلات الملغاة التي لم يتم تأكيدها
    frappe.db.sql("""
        UPDATE `tabTrip`
        SET `status` = 'ملغاة'
        WHERE `trip_date` < CURDATE() AND `status` = 'مؤقتة'
    """)
