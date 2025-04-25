# نظام حجز التذاكر

نظام متكامل لإدارة حجز تذاكر الرحلات مبني على منصة ERPNext.

## نظرة عامة

نظام حجز التذاكر هو تطبيق شامل يوفر حلاً متكاملاً لشركات النقل لإدارة الرحلات والحجوزات والتذاكر. يتيح النظام البحث عن الرحلات المتاحة، وحجز المقاعد، وإصدار التذاكر، وإدارة الوكلاء، وإنشاء التقارير المختلفة.

## الميزات الرئيسية

- **إدارة الرحلات**: إنشاء وتعديل وإلغاء الرحلات مع تحديد المسارات والمواعيد والأسعار.
- **البحث عن الرحلات**: البحث عن الرحلات المتاحة حسب المدينة المصدر والوجهة والتاريخ ونوع المركبة.
- **إدارة الحجوزات**: إنشاء وتعديل وإلغاء الحجوزات مع إمكانية اختيار المقاعد.
- **إدارة التذاكر**: إصدار وطباعة وإلغاء التذاكر مع دعم رموز QR للتحقق.
- **إدارة الوكلاء**: إدارة الوكلاء وعمولاتهم وكشوف حساباتهم.
- **التقارير**: إنشاء تقارير متنوعة مثل تقارير المبيعات والرحلات وأداء الوكلاء والتقارير المالية.
- **لوحة التحكم**: عرض إحصائيات ومؤشرات الأداء الرئيسية.

## المتطلبات الأساسية

- ERPNext الإصدار 13 أو أحدث
- Python 3.7 أو أحدث
- Node.js 14 أو أحدث
- MariaDB 10.3 أو أحدث

## التثبيت

يرجى الرجوع إلى [دليل التثبيت](./docs/installation_guide.md) للحصول على تعليمات مفصلة حول كيفية تثبيت وإعداد النظام.

إذا كنت تستخدم نظام ERPNext موجود بالفعل، يرجى الرجوع إلى [دليل التثبيت على نظام ERPNext موجود](./docs/installation_guide_for_existing_erpnext.md).

## الوثائق

- [هيكل قاعدة البيانات](./database_schema.md)
- [هيكل النظام](./system_architecture.md)
- [وحدة البحث عن الرحلات](./trip_search_module.md)
- [وحدة إدارة التذاكر](./ticket_management_module.md)
- [سير عمل طلبات الوكلاء](./agent_request_workflow.md)
- [واجهة البحث عن الرحلات](./trip_search_interface.md)
- [واجهة تقديم طلبات الوكلاء](./agent_request_submission_interface.md)
- [كشف حساب الوكيل](./agent_account_statement.md)
- [مخطط المقاعد وبيانات الركاب](./seating_chart_passenger_data.md)
- [واجهة موافقة المدير](./manager_approval_interface.md)
- [وحدة طباعة التذاكر](./ticket_printing_module.md)

## هيكل التطبيق

```
ticket_system/
├── controllers/           # وحدات التحكم الأساسية
│   ├── trip_controller.py
│   ├── booking_controller.py
│   ├── ticket_controller.py
│   └── agent_controller.py
├── models/                # نماذج البيانات (Doctypes)
│   └── doctype/
│       ├── city/
│       ├── route/
│       ├── trip/
│       ├── ticket/
│       ├── agent/
│       ├── customer/
│       ├── booking/
│       ├── booking_seat/
│       ├── payment/
│       ├── vehicle/
│       ├── seat/
│       └── trip_seat_status/
├── public/                # الملفات العامة
│   ├── css/
│   │   └── ticket_system.css
│   └── js/
│       └── ticket_system.js
├── reports/               # وحدات التقارير
│   └── reports.py
├── setup/                 # سكريبتات التثبيت والإعداد
│   ├── install.py
│   ├── setup.py
│   ├── update.py
│   └── maintenance.py
├── templates/             # قوالب HTML
│   ├── pages/
│   │   ├── trip_search.html
│   │   ├── booking.html
│   │   ├── ticket_management.html
│   │   ├── agent_management.html
│   │   ├── dashboard.html
│   │   └── ticket_system_setup.html
│   ├── reports/
│   │   ├── sales_report.html
│   │   ├── trips_report.html
│   │   ├── agents_report.html
│   │   └── financial_report.html
│   └── ticket_template.html
├── docs/                  # الوثائق
│   ├── installation_guide.md
│   └── installation_guide_for_existing_erpnext.md
├── api.py                 # واجهة برمجة التطبيقات
├── hooks.py               # خطافات ERPNext
└── __init__.py
```

## المساهمة

نرحب بالمساهمات! يرجى قراءة [إرشادات المساهمة](./CONTRIBUTING.md) للحصول على مزيد من المعلومات.

## الترخيص

هذا المشروع مرخص بموجب [رخصة MIT](./LICENSE).

## الدعم

إذا كنت بحاجة إلى مساعدة، يرجى التواصل مع فريق الدعم الفني:

- البريد الإلكتروني: support@example.com
- رقم الهاتف: +123456789
- موقع الدعم الفني: https://support.example.com
# ticket_system
