// نظام حجز التذاكر - ملف JavaScript الرئيسي

frappe.provide("ticket_system");

// تهيئة النظام
ticket_system = {
    // الإعدادات العامة
    settings: {
        dateFormat: "YYYY-MM-DD",
        timeFormat: "HH:mm",
        currency: "ريال يمني",
        defaultVehicleType: "سياحي (VIP)"
    },
    
    // تهيئة النظام
    init: function() {
        // تهيئة الأحداث العامة
        this.bindEvents();
        
        // تهيئة الصفحات المختلفة بناءً على المسار الحالي
        const currentPath = window.location.pathname;
        
        if (currentPath.includes("trip-search")) {
            this.tripSearch.init();
        } else if (currentPath.includes("booking")) {
            this.booking.init();
        } else if (currentPath.includes("ticket")) {
            this.ticket.init();
        } else if (currentPath.includes("agent")) {
            this.agent.init();
        } else if (currentPath.includes("dashboard")) {
            this.dashboard.init();
        }
    },
    
    // ربط الأحداث العامة
    bindEvents: function() {
        // تحديث التاريخ والوقت في الصفحة
        setInterval(function() {
            const now = moment();
            $(".current-date").text(now.format("YYYY-MM-DD"));
            $(".current-time").text(now.format("HH:mm:ss"));
        }, 1000);
        
        // أحداث النموذج العامة
        $(document).on("submit", "form.ticket-system-form", function(e) {
            e.preventDefault();
            const formId = $(this).attr("id");
            
            if (formId === "trip-search-form") {
                ticket_system.tripSearch.search();
            } else if (formId === "booking-form") {
                ticket_system.booking.createBooking();
            } else if (formId === "ticket-search-form") {
                ticket_system.ticket.search();
            } else if (formId === "agent-search-form") {
                ticket_system.agent.search();
            }
        });
    },
    
    // وحدة البحث عن الرحلات
    tripSearch: {
        init: function() {
            this.bindEvents();
            this.initDatePickers();
        },
        
        bindEvents: function() {
            // حدث تغيير المدينة المصدر
            $("#from-city").on("change", function() {
                const fromCity = $(this).val();
                ticket_system.tripSearch.updateDestinations(fromCity);
            });
            
            // حدث النقر على رحلة
            $(document).on("click", ".trip-details-btn", function() {
                const tripId = $(this).data("trip-id");
                ticket_system.tripSearch.showTripDetails(tripId);
            });
            
            // حدث النقر على زر الحجز
            $(document).on("click", ".book-trip-btn", function() {
                const tripId = $(this).data("trip-id");
                window.location.href = `/ticket-system/booking?trip=${tripId}`;
            });
        },
        
        initDatePickers: function() {
            // تهيئة حقول التاريخ
            $(".date-picker").datepicker({
                dateFormat: "yy-mm-dd",
                minDate: 0,
                changeMonth: true,
                changeYear: true
            });
            
            // تعيين تاريخ اليوم كقيمة افتراضية
            const today = moment().format("YYYY-MM-DD");
            $("#trip-date").val(today);
        },
        
        updateDestinations: function(fromCity) {
            if (!fromCity) return;
            
            // الحصول على الوجهات المتاحة من المدينة المصدر
            frappe.call({
                method: "ticket_system.api.get_available_destinations",
                args: {
                    from_city: fromCity
                },
                callback: function(response) {
                    if (response.message) {
                        const destinations = response.message;
                        let options = '<option value="">اختر الوجهة</option>';
                        
                        destinations.forEach(function(dest) {
                            options += `<option value="${dest.name}">${dest.city_name}</option>`;
                        });
                        
                        $("#to-city").html(options);
                    }
                }
            });
        },
        
        search: function() {
            const fromCity = $("#from-city").val();
            const toCity = $("#to-city").val();
            const tripDate = $("#trip-date").val();
            const vehicleType = $("#vehicle-type").val();
            
            if (!fromCity || !toCity || !tripDate) {
                ticket_system.showAlert("يرجى تحديد المدينة المصدر والوجهة والتاريخ", "warning");
                return;
            }
            
            // عرض مؤشر التحميل
            $("#search-results").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>جاري البحث...</p></div>');
            
            // البحث عن الرحلات
            frappe.call({
                method: "ticket_system.api.search_trips",
                args: {
                    source_city: fromCity,
                    destination_city: toCity,
                    trip_date: tripDate,
                    vehicle_type: vehicleType
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.tripSearch.renderSearchResults(response.message);
                    } else {
                        $("#search-results").html('<div class="alert ticket-system-alert ticket-system-alert-info">لا توجد رحلات متاحة للمعايير المحددة</div>');
                    }
                }
            });
        },
        
        renderSearchResults: function(trips) {
            if (!trips || trips.length === 0) {
                $("#search-results").html('<div class="alert ticket-system-alert ticket-system-alert-info">لا توجد رحلات متاحة للمعايير المحددة</div>');
                return;
            }
            
            let html = '<div class="ticket-system-trips">';
            
            trips.forEach(function(trip) {
                html += `
                <div class="ticket-system-trip-card">
                    <div class="ticket-system-trip-header">
                        <div class="ticket-system-trip-title">
                            ${trip.from_city} إلى ${trip.to_city}
                        </div>
                        <div class="ticket-system-trip-price">
                            ${trip.price} ${trip.currency}
                        </div>
                    </div>
                    <div class="ticket-system-trip-details">
                        <div class="ticket-system-trip-detail">
                            <div class="ticket-system-trip-detail-label">رقم الرحلة</div>
                            <div class="ticket-system-trip-detail-value">${trip.trip_code}</div>
                        </div>
                        <div class="ticket-system-trip-detail">
                            <div class="ticket-system-trip-detail-label">تاريخ الرحلة</div>
                            <div class="ticket-system-trip-detail-value">${trip.trip_date}</div>
                        </div>
                        <div class="ticket-system-trip-detail">
                            <div class="ticket-system-trip-detail-label">وقت المغادرة</div>
                            <div class="ticket-system-trip-detail-value">${trip.departure_time}</div>
                        </div>
                        <div class="ticket-system-trip-detail">
                            <div class="ticket-system-trip-detail-label">وقت الوصول</div>
                            <div class="ticket-system-trip-detail-value">${trip.arrival_time}</div>
                        </div>
                        <div class="ticket-system-trip-detail">
                            <div class="ticket-system-trip-detail-label">نوع المركبة</div>
                            <div class="ticket-system-trip-detail-value">${trip.vehicle_type}</div>
                        </div>
                        <div class="ticket-system-trip-detail">
                            <div class="ticket-system-trip-detail-label">المقاعد المتاحة</div>
                            <div class="ticket-system-trip-detail-value">${trip.available_seats} / ${trip.total_seats}</div>
                        </div>
                    </div>
                    <div class="ticket-system-trip-actions">
                        <button class="ticket-system-btn ticket-system-btn-secondary trip-details-btn" data-trip-id="${trip.name}">تفاصيل</button>
                        <button class="ticket-system-btn ticket-system-btn-primary book-trip-btn" data-trip-id="${trip.name}">حجز</button>
                    </div>
                </div>
                `;
            });
            
            html += '</div>';
            $("#search-results").html(html);
        },
        
        showTripDetails: function(tripId) {
            frappe.call({
                method: "ticket_system.api.get_trip_details",
                args: {
                    trip: tripId
                },
                callback: function(response) {
                    if (response.message) {
                        const tripDetails = response.message;
                        
                        // إنشاء محتوى النافذة المنبثقة
                        let modalContent = `
                        <div class="modal-header">
                            <h5 class="modal-title">تفاصيل الرحلة: ${tripDetails.trip.trip_code}</h5>
                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="ticket-system-trip-details">
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">المسار</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.from_city_name} إلى ${tripDetails.to_city_name}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">تاريخ الرحلة</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.trip_date}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">وقت المغادرة</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.departure_time}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">وقت الوصول</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.arrival_time}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">المسافة</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.route.distance} كم</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">الوقت المقدر</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.route.estimated_time} ساعة</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">نوع المركبة</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.vehicle_type}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">السعر</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.price} ${tripDetails.trip.currency}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">المقاعد المتاحة</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.available_seats} / ${tripDetails.trip.total_seats}</div>
                                </div>
                                <div class="ticket-system-trip-detail">
                                    <div class="ticket-system-trip-detail-label">الحالة</div>
                                    <div class="ticket-system-trip-detail-value">${tripDetails.trip.status}</div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="ticket-system-btn ticket-system-btn-secondary" data-dismiss="modal">إغلاق</button>
                            <button type="button" class="ticket-system-btn ticket-system-btn-primary book-trip-btn" data-trip-id="${tripDetails.trip.name}" data-dismiss="modal">حجز</button>
                        </div>
                        `;
                        
                        // عرض النافذة المنبثقة
                        frappe.msgprint({
                            title: __("تفاصيل الرحلة"),
                            indicator: "blue",
                            message: modalContent
                        });
                    }
                }
            });
        }
    },
    
    // وحدة إدارة الحجوزات
    booking: {
        selectedSeats: [],
        
        init: function() {
            this.bindEvents();
            this.loadTripDetails();
        },
        
        bindEvents: function() {
            // حدث النقر على مقعد
            $(document).on("click", ".ticket-system-seat", function() {
                if ($(this).hasClass("ticket-system-seat-unavailable")) {
                    return;
                }
                
                const seatNumber = $(this).data("seat-number");
                
                if ($(this).hasClass("ticket-system-seat-selected")) {
                    // إلغاء تحديد المقعد
                    $(this).removeClass("ticket-system-seat-selected");
                    ticket_system.booking.removeSelectedSeat(seatNumber);
                } else {
                    // تحديد المقعد
                    $(this).addClass("ticket-system-seat-selected");
                    ticket_system.booking.addSelectedSeat(seatNumber);
                }
                
                // تحديث نموذج الحجز
                ticket_system.booking.updateBookingForm();
            });
            
            // حدث إضافة راكب
            $("#add-passenger-btn").on("click", function() {
                ticket_system.booking.addPassengerForm();
            });
            
            // حدث إزالة راكب
            $(document).on("click", ".remove-passenger-btn", function() {
                const index = $(this).data("index");
                ticket_system.booking.removePassengerForm(index);
            });
        },
        
        loadTripDetails: function() {
            const urlParams = new URLSearchParams(window.location.search);
            const tripId = urlParams.get("trip");
            
            if (!tripId) {
                ticket_system.showAlert("لم يتم تحديد رحلة", "danger");
                return;
            }
            
            // الحصول على تفاصيل الرحلة
            frappe.call({
                method: "ticket_system.api.get_trip_details",
                args: {
                    trip: tripId
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.booking.renderTripDetails(response.message);
                        ticket_system.booking.loadSeatMap(tripId);
                    } else {
                        ticket_system.showAlert("لا يمكن الحصول على تفاصيل الرحلة", "danger");
                    }
                }
            });
        },
        
        renderTripDetails: function(tripDetails) {
            // عرض تفاصيل الرحلة
            $("#trip-details").html(`
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">
                        ${tripDetails.from_city_name} إلى ${tripDetails.to_city_name}
                    </div>
                    <div class="ticket-system-subtitle">
                        رقم الرحلة: ${tripDetails.trip.trip_code} | التاريخ: ${tripDetails.trip.trip_date}
                    </div>
                </div>
                <div class="ticket-system-trip-details">
                    <div class="ticket-system-trip-detail">
                        <div class="ticket-system-trip-detail-label">وقت المغادرة</div>
                        <div class="ticket-system-trip-detail-value">${tripDetails.trip.departure_time}</div>
                    </div>
                    <div class="ticket-system-trip-detail">
                        <div class="ticket-system-trip-detail-label">وقت الوصول</div>
                        <div class="ticket-system-trip-detail-value">${tripDetails.trip.arrival_time}</div>
                    </div>
                    <div class="ticket-system-trip-detail">
                        <div class="ticket-system-trip-detail-label">نوع المركبة</div>
                        <div class="ticket-system-trip-detail-value">${tripDetails.trip.vehicle_type}</div>
                    </div>
                    <div class="ticket-system-trip-detail">
                        <div class="ticket-system-trip-detail-label">السعر</div>
                        <div class="ticket-system-trip-detail-value">${tripDetails.trip.price} ${tripDetails.trip.currency}</div>
                    </div>
                </div>
            </div>
            `);
            
            // تخزين معرف الرحلة في النموذج
            $("#trip-id").val(tripDetails.trip.name);
            $("#trip-price").val(tripDetails.trip.price);
            $("#trip-currency").val(tripDetails.trip.currency);
        },
        
        loadSeatMap: function(tripId) {
            // الحصول على مخطط المقاعد للرحلة
            frappe.call({
                method: "ticket_system.api.get_available_seats",
                args: {
                    trip: tripId
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.booking.renderSeatMap(response.message);
                    } else {
                        $("#seat-map").html('<div class="alert ticket-system-alert ticket-system-alert-info">لا توجد معلومات عن المقاعد</div>');
                    }
                }
            });
        },
        
        renderSeatMap: function(seats) {
            // تحديد العدد الإجمالي للمقاعد
            const totalSeats = Math.max(...seats.map(seat => seat.seat_number), 0);
            
            // إنشاء مصفوفة لجميع المقاعد
            const allSeats = [];
            for (let i = 1; i <= totalSeats; i++) {
                const seat = seats.find(s => s.seat_number === i);
                
                if (seat) {
                    allSeats.push({
                        seat_number: i,
                        status: seat.status,
                        price: seat.price,
                        seat_type: seat.seat_type
                    });
                } else {
                    allSeats.push({
                        seat_number: i,
                        status: "غير متاح",
                        price: 0,
                        seat_type: "غير معروف"
                    });
                }
            }
            
            // عرض مخطط المقاعد
            let html = '<div class="ticket-system-seat-map">';
            
            allSeats.forEach(function(seat) {
                let seatClass = "ticket-system-seat";
                
                if (seat.status === "متاح") {
                    seatClass += " ticket-system-seat-available";
                } else {
                    seatClass += " ticket-system-seat-unavailable";
                }
                
                html += `
                <div class="${seatClass}" data-seat-number="${seat.seat_number}" data-seat-price="${seat.price}" data-seat-type="${seat.seat_type}">
                    <div class="seat-number">${seat.seat_number}</div>
                    <div class="seat-type">${seat.seat_type}</div>
                    <div class="seat-price">${seat.price}</div>
                </div>
                `;
            });
            
            html += '</div>';
            
            // إضافة مفتاح المخطط
            html += `
            <div class="seat-map-legend">
                <div class="legend-item">
                    <div class="ticket-system-seat ticket-system-seat-available legend-sample"></div>
                    <div class="legend-text">متاح</div>
                </div>
                <div class="legend-item">
                    <div class="ticket-system-seat ticket-system-seat-selected legend-sample"></div>
                    <div class="legend-text">محدد</div>
                </div>
                <div class="legend-item">
                    <div class="ticket-system-seat ticket-system-seat-unavailable legend-sample"></div>
                    <div class="legend-text">غير متاح</div>
                </div>
            </div>
            `;
            
            $("#seat-map").html(html);
        },
        
        addSelectedSeat: function(seatNumber) {
            const seatElement = $(`.ticket-system-seat[data-seat-number="${seatNumber}"]`);
            const seatPrice = seatElement.data("seat-price");
            const seatType = seatElement.data("seat-type");
            
            this.selectedSeats.push({
                seat_number: seatNumber,
                price: seatPrice,
                seat_type: seatType
            });
        },
        
        removeSelectedSeat: function(seatNumber) {
            this.selectedSeats = this.selectedSeats.filter(seat => seat.seat_number != seatNumber);
        },
        
        updateBookingForm: function() {
            // تحديث عدد المقاعد المحددة
            $("#selected-seats-count").text(this.selectedSeats.length);
            
            // حساب المبلغ الإجمالي
            const totalAmount = this.selectedSeats.reduce((total, seat) => total + seat.price, 0);
            $("#total-amount").text(totalAmount);
            
            // تحديث نماذج الركاب
            this.updatePassengerForms();
        },
        
        updatePassengerForms: function() {
            const passengerFormsContainer = $("#passenger-forms");
            const currentForms = passengerFormsContainer.find(".passenger-form").length;
            
            // إضافة نماذج إضافية إذا لزم الأمر
            if (this.selectedSeats.length > currentForms) {
                for (let i = currentForms; i < this.selectedSeats.length; i++) {
                    this.addPassengerForm();
                }
            }
            
            // إزالة النماذج الزائدة
            if (this.selectedSeats.length < currentForms) {
                for (let i = currentForms - 1; i >= this.selectedSeats.length; i--) {
                    this.removePassengerForm(i);
                }
            }
            
            // تحديث أرقام المقاعد في النماذج
            $(".passenger-form").each((index, form) => {
                if (index < this.selectedSeats.length) {
                    $(form).find(".seat-number-display").text(this.selectedSeats[index].seat_number);
                    $(form).find("input[name='seat_number[]']").val(this.selectedSeats[index].seat_number);
                    $(form).find("input[name='seat_price[]']").val(this.selectedSeats[index].price);
                }
            });
        },
        
        addPassengerForm: function() {
            const index = $(".passenger-form").length;
            const seatNumber = this.selectedSeats[index] ? this.selectedSeats[index].seat_number : "";
            const seatPrice = this.selectedSeats[index] ? this.selectedSeats[index].price : 0;
            
            const formHtml = `
            <div class="passenger-form ticket-system-card" data-index="${index}">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">
                        بيانات الراكب - مقعد رقم <span class="seat-number-display">${seatNumber}</span>
                    </div>
                    ${index > 0 ? `<button type="button" class="ticket-system-btn ticket-system-btn-danger remove-passenger-btn" data-index="${index}">إزالة</button>` : ''}
                </div>
                <input type="hidden" name="seat_number[]" value="${seatNumber}">
                <input type="hidden" name="seat_price[]" value="${seatPrice}">
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="passenger-name-${index}">اسم الراكب</label>
                    <input type="text" class="ticket-system-input" id="passenger-name-${index}" name="passenger_name[]" required>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="passenger-id-type-${index}">نوع الهوية</label>
                    <select class="ticket-system-select" id="passenger-id-type-${index}" name="passenger_id_type[]" required>
                        <option value="">اختر نوع الهوية</option>
                        <option value="بطاقة شخصية">بطاقة شخصية</option>
                        <option value="جواز سفر">جواز سفر</option>
                        <option value="رخصة قيادة">رخصة قيادة</option>
                        <option value="أخرى">أخرى</option>
                    </select>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="passenger-id-number-${index}">رقم الهوية</label>
                    <input type="text" class="ticket-system-input" id="passenger-id-number-${index}" name="passenger_id_number[]" required>
                </div>
            </div>
            `;
            
            $("#passenger-forms").append(formHtml);
        },
        
        removePassengerForm: function(index) {
            $(`.passenger-form[data-index="${index}"]`).remove();
            
            // إعادة ترقيم النماذج المتبقية
            $(".passenger-form").each((i, form) => {
                $(form).attr("data-index", i);
                $(form).find(".remove-passenger-btn").attr("data-index", i);
            });
        },
        
        createBooking: function() {
            // التحقق من صحة النموذج
            if (!this.validateBookingForm()) {
                return;
            }
            
            // جمع بيانات الحجز
            const tripId = $("#trip-id").val();
            const customerId = $("#customer-id").val();
            const agentId = $("#agent-id").val();
            const paymentMethod = $("#payment-method").val();
            const paidAmount = parseFloat($("#paid-amount").val()) || 0;
            const notes = $("#booking-notes").val();
            
            // جمع بيانات الركاب
            const seats = [];
            $(".passenger-form").each((index, form) => {
                seats.push({
                    seat_number: $(form).find("input[name='seat_number[]']").val(),
                    passenger_name: $(form).find("input[name='passenger_name[]']").val(),
                    passenger_id_type: $(form).find("select[name='passenger_id_type[]']").val(),
                    passenger_id_number: $(form).find("input[name='passenger_id_number[]']").val()
                });
            });
            
            // عرض مؤشر التحميل
            $("#booking-result").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>جاري إنشاء الحجز...</p></div>');
            
            // إنشاء الحجز
            frappe.call({
                method: "ticket_system.api.create_booking",
                args: {
                    customer: customerId,
                    trip: tripId,
                    seats: seats,
                    agent: agentId || null,
                    payment_method: paymentMethod,
                    paid_amount: paidAmount,
                    notes: notes
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.booking.showBookingConfirmation(response.message);
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء إنشاء الحجز", "danger");
                    }
                }
            });
        },
        
        validateBookingForm: function() {
            // التحقق من تحديد مقاعد
            if (this.selectedSeats.length === 0) {
                ticket_system.showAlert("يرجى تحديد مقعد واحد على الأقل", "warning");
                return false;
            }
            
            // التحقق من إدخال بيانات العميل
            if (!$("#customer-id").val()) {
                ticket_system.showAlert("يرجى تحديد العميل", "warning");
                return false;
            }
            
            // التحقق من إدخال بيانات الركاب
            let isValid = true;
            $(".passenger-form").each((index, form) => {
                const passengerName = $(form).find("input[name='passenger_name[]']").val();
                const passengerIdType = $(form).find("select[name='passenger_id_type[]']").val();
                const passengerIdNumber = $(form).find("input[name='passenger_id_number[]']").val();
                
                if (!passengerName || !passengerIdType || !passengerIdNumber) {
                    ticket_system.showAlert(`يرجى إدخال جميع بيانات الراكب للمقعد رقم ${this.selectedSeats[index].seat_number}`, "warning");
                    isValid = false;
                    return false;
                }
            });
            
            return isValid;
        },
        
        showBookingConfirmation: function(booking) {
            // عرض تأكيد الحجز
            let html = `
            <div class="ticket-system-alert ticket-system-alert-success">
                <h4>تم إنشاء الحجز بنجاح!</h4>
                <p>رقم الحجز: ${booking.booking_number}</p>
                <p>المبلغ الإجمالي: ${booking.total_amount} ${booking.currency}</p>
                <p>حالة الحجز: ${booking.booking_status}</p>
                <p>حالة الدفع: ${booking.payment_status}</p>
            </div>
            `;
            
            // إضافة روابط للإجراءات
            html += `
            <div class="booking-actions">
                <a href="/ticket-system/booking/${booking.name}" class="ticket-system-btn ticket-system-btn-primary">عرض تفاصيل الحجز</a>
                ${booking.booking_status === "مؤكد" ? `<a href="/ticket-system/print-tickets/${booking.name}" class="ticket-system-btn ticket-system-btn-secondary">طباعة التذاكر</a>` : ''}
                <a href="/ticket-system/trip-search" class="ticket-system-btn ticket-system-btn-secondary">بحث جديد</a>
            </div>
            `;
            
            $("#booking-form-container").hide();
            $("#booking-result").html(html);
        }
    },
    
    // وحدة إدارة التذاكر
    ticket: {
        init: function() {
            this.bindEvents();
        },
        
        bindEvents: function() {
            // حدث البحث عن تذكرة
            $("#ticket-search-btn").on("click", function() {
                const ticketNumber = $("#ticket-number").val();
                if (ticketNumber) {
                    ticket_system.ticket.searchTicket(ticketNumber);
                } else {
                    ticket_system.showAlert("يرجى إدخال رقم التذكرة", "warning");
                }
            });
            
            // حدث تحديد التذكرة كمستخدمة
            $(document).on("click", "#mark-ticket-used-btn", function() {
                const ticketNumber = $(this).data("ticket-number");
                ticket_system.ticket.markTicketAsUsed(ticketNumber);
            });
            
            // حدث إلغاء التذكرة
            $(document).on("click", "#cancel-ticket-btn", function() {
                const ticketNumber = $(this).data("ticket-number");
                ticket_system.ticket.showCancelTicketForm(ticketNumber);
            });
            
            // حدث طباعة التذكرة
            $(document).on("click", "#print-ticket-btn", function() {
                const ticketNumber = $(this).data("ticket-number");
                ticket_system.ticket.printTicket(ticketNumber);
            });
        },
        
        searchTicket: function(ticketNumber) {
            // عرض مؤشر التحميل
            $("#ticket-details").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>جاري البحث...</p></div>');
            
            // البحث عن التذكرة
            frappe.call({
                method: "ticket_system.api.validate_ticket",
                args: {
                    ticket_number: ticketNumber
                },
                callback: function(response) {
                    if (response.message) {
                        const result = response.message;
                        
                        if (result.status === "غير موجودة") {
                            ticket_system.showAlert("التذكرة غير موجودة", "danger");
                            $("#ticket-details").html('');
                        } else {
                            ticket_system.ticket.getTicketDetails(result.ticket.name);
                        }
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء البحث عن التذكرة", "danger");
                        $("#ticket-details").html('');
                    }
                }
            });
        },
        
        getTicketDetails: function(ticketName) {
            frappe.call({
                method: "ticket_system.api.get_ticket_details",
                args: {
                    ticket: ticketName
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.ticket.renderTicketDetails(response.message);
                    } else {
                        ticket_system.showAlert("لا يمكن الحصول على تفاصيل التذكرة", "danger");
                        $("#ticket-details").html('');
                    }
                }
            });
        },
        
        renderTicketDetails: function(ticketDetails) {
            // تحديد لون الحالة
            let statusClass = "";
            switch (ticketDetails.ticket.status) {
                case "صالحة":
                    statusClass = "text-success";
                    break;
                case "مستخدمة":
                    statusClass = "text-warning";
                    break;
                case "ملغاة":
                    statusClass = "text-danger";
                    break;
                default:
                    statusClass = "text-secondary";
            }
            
            // عرض تفاصيل التذكرة
            let html = `
            <div class="ticket-system-ticket">
                <div class="ticket-system-ticket-header">
                    <div class="ticket-system-ticket-title">
                        ${ticketDetails.from_city_name} إلى ${ticketDetails.to_city_name}
                    </div>
                    <div class="ticket-system-ticket-number">
                        رقم التذكرة: ${ticketDetails.ticket.ticket_number}
                    </div>
                </div>
                <div class="ticket-system-ticket-details">
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">اسم الراكب</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.ticket.passenger_name}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">رقم المقعد</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.ticket.seat_number}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">رقم الرحلة</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.trip.trip_code}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">تاريخ الرحلة</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.trip.trip_date}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">وقت المغادرة</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.trip.departure_time}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">وقت الوصول</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.trip.arrival_time}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">السعر</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.ticket.price} ${ticketDetails.ticket.currency}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">تاريخ الإصدار</div>
                        <div class="ticket-system-trip-detail-value">${ticketDetails.ticket.issue_date}</div>
                    </div>
                    <div class="ticket-system-ticket-detail">
                        <div class="ticket-system-trip-detail-label">الحالة</div>
                        <div class="ticket-system-trip-detail-value ${statusClass}">${ticketDetails.ticket.status}</div>
                    </div>
                </div>
                <div class="ticket-system-ticket-actions">
                    ${ticketDetails.ticket.status === "صالحة" ? `
                    <button id="mark-ticket-used-btn" class="ticket-system-btn ticket-system-btn-secondary" data-ticket-number="${ticketDetails.ticket.ticket_number}">تحديد كمستخدمة</button>
                    <button id="cancel-ticket-btn" class="ticket-system-btn ticket-system-btn-danger" data-ticket-number="${ticketDetails.ticket.ticket_number}">إلغاء التذكرة</button>
                    ` : ''}
                    <button id="print-ticket-btn" class="ticket-system-btn ticket-system-btn-primary" data-ticket-number="${ticketDetails.ticket.ticket_number}">طباعة التذكرة</button>
                </div>
            </div>
            `;
            
            $("#ticket-details").html(html);
        },
        
        markTicketAsUsed: function(ticketNumber) {
            frappe.call({
                method: "ticket_system.api.mark_ticket_as_used",
                args: {
                    ticket_number: ticketNumber
                },
                callback: function(response) {
                    if (response.message) {
                        const result = response.message;
                        
                        if (result.status === "نجاح") {
                            ticket_system.showAlert(result.message, "success");
                            ticket_system.ticket.searchTicket(ticketNumber);
                        } else {
                            ticket_system.showAlert(result.message, "danger");
                        }
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء تحديث حالة التذكرة", "danger");
                    }
                }
            });
        },
        
        showCancelTicketForm: function(ticketNumber) {
            // إنشاء نموذج إلغاء التذكرة
            let formHtml = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">إلغاء التذكرة</div>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="cancel-reason">سبب الإلغاء</label>
                    <textarea class="ticket-system-input" id="cancel-reason" rows="3" required></textarea>
                </div>
                <div class="ticket-system-form-actions">
                    <button id="confirm-cancel-btn" class="ticket-system-btn ticket-system-btn-danger" data-ticket-number="${ticketNumber}">تأكيد الإلغاء</button>
                    <button id="cancel-cancel-btn" class="ticket-system-btn ticket-system-btn-secondary">إلغاء</button>
                </div>
            </div>
            `;
            
            // عرض النموذج
            $("#cancel-ticket-form").html(formHtml).show();
            
            // ربط الأحداث
            $("#confirm-cancel-btn").on("click", function() {
                const reason = $("#cancel-reason").val();
                if (reason) {
                    ticket_system.ticket.cancelTicket(ticketNumber, reason);
                } else {
                    ticket_system.showAlert("يرجى إدخال سبب الإلغاء", "warning");
                }
            });
            
            $("#cancel-cancel-btn").on("click", function() {
                $("#cancel-ticket-form").html('').hide();
            });
        },
        
        cancelTicket: function(ticketNumber, reason) {
            frappe.call({
                method: "ticket_system.api.cancel_ticket",
                args: {
                    ticket_number: ticketNumber,
                    reason: reason
                },
                callback: function(response) {
                    if (response.message) {
                        const result = response.message;
                        
                        if (result.status === "نجاح") {
                            ticket_system.showAlert(result.message, "success");
                            $("#cancel-ticket-form").html('').hide();
                            ticket_system.ticket.searchTicket(ticketNumber);
                        } else {
                            ticket_system.showAlert(result.message, "danger");
                        }
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء إلغاء التذكرة", "danger");
                    }
                }
            });
        },
        
        printTicket: function(ticketNumber) {
            frappe.call({
                method: "ticket_system.api.print_ticket",
                args: {
                    ticket_number: ticketNumber
                },
                callback: function(response) {
                    if (response.message) {
                        const pdfPath = response.message;
                        window.open(`/files/${pdfPath}`, '_blank');
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء طباعة التذكرة", "danger");
                    }
                }
            });
        }
    },
    
    // وحدة إدارة الوكلاء
    agent: {
        init: function() {
            this.bindEvents();
        },
        
        bindEvents: function() {
            // حدث البحث عن وكيل
            $("#agent-search-btn").on("click", function() {
                const agentId = $("#agent-id").val();
                if (agentId) {
                    ticket_system.agent.getAgentDetails(agentId);
                } else {
                    ticket_system.showAlert("يرجى تحديد الوكيل", "warning");
                }
            });
            
            // حدث عرض كشف الحساب
            $(document).on("click", "#view-statement-btn", function() {
                const agentId = $(this).data("agent-id");
                ticket_system.agent.showStatementForm(agentId);
            });
            
            // حدث إنشاء دفعة
            $(document).on("click", "#create-payment-btn", function() {
                const agentId = $(this).data("agent-id");
                ticket_system.agent.showPaymentForm(agentId);
            });
        },
        
        getAgentDetails: function(agentId) {
            // عرض مؤشر التحميل
            $("#agent-details").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>جاري تحميل البيانات...</p></div>');
            
            // الحصول على تفاصيل الوكيل
            frappe.call({
                method: "ticket_system.api.get_agent_details",
                args: {
                    agent: agentId
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.agent.renderAgentDetails(response.message);
                    } else {
                        ticket_system.showAlert("لا يمكن الحصول على تفاصيل الوكيل", "danger");
                        $("#agent-details").html('');
                    }
                }
            });
        },
        
        renderAgentDetails: function(agentDetails) {
            // تحديد لون الحالة
            let statusClass = agentDetails.agent.status === "نشط" ? "text-success" : "text-danger";
            
            // عرض تفاصيل الوكيل
            let html = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">
                        ${agentDetails.agent.agent_name}
                    </div>
                    <div class="ticket-system-subtitle">
                        رمز الوكيل: ${agentDetails.agent.agent_code} | 
                        <span class="${statusClass}">الحالة: ${agentDetails.agent.status}</span>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">نوع الوكيل</label>
                            <div>${agentDetails.agent.agent_type}</div>
                        </div>
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">البريد الإلكتروني</label>
                            <div>${agentDetails.agent.email || "غير محدد"}</div>
                        </div>
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">رقم الهاتف</label>
                            <div>${agentDetails.agent.phone}</div>
                        </div>
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">العنوان</label>
                            <div>${agentDetails.agent.address || "غير محدد"}</div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">نسبة العمولة</label>
                            <div>${agentDetails.agent.commission_rate}%</div>
                        </div>
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">حد الائتمان</label>
                            <div>${agentDetails.agent.credit_limit}</div>
                        </div>
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label">الرصيد الحالي</label>
                            <div>${agentDetails.agent.current_balance}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">
                        إحصائيات المبيعات
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-3">
                        <div class="ticket-system-stat-card">
                            <div class="stat-value">${agentDetails.sales_statistics.total_bookings}</div>
                            <div class="stat-label">إجمالي الحجوزات</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="ticket-system-stat-card">
                            <div class="stat-value">${agentDetails.sales_statistics.total_tickets}</div>
                            <div class="stat-label">إجمالي التذاكر</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="ticket-system-stat-card">
                            <div class="stat-value">${agentDetails.sales_statistics.total_sales}</div>
                            <div class="stat-label">إجمالي المبيعات</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="ticket-system-stat-card">
                            <div class="stat-value">${agentDetails.sales_statistics.total_commission}</div>
                            <div class="stat-label">إجمالي العمولات</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="ticket-system-actions">
                <button id="view-statement-btn" class="ticket-system-btn ticket-system-btn-secondary" data-agent-id="${agentDetails.agent.name}">عرض كشف الحساب</button>
                <button id="create-payment-btn" class="ticket-system-btn ticket-system-btn-primary" data-agent-id="${agentDetails.agent.name}">إنشاء دفعة</button>
            </div>
            `;
            
            $("#agent-details").html(html);
        },
        
        showStatementForm: function(agentId) {
            // إنشاء نموذج كشف الحساب
            let formHtml = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">كشف حساب الوكيل</div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label" for="from-date">من تاريخ</label>
                            <input type="date" class="ticket-system-input date-picker" id="from-date">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="ticket-system-form-group">
                            <label class="ticket-system-label" for="to-date">إلى تاريخ</label>
                            <input type="date" class="ticket-system-input date-picker" id="to-date">
                        </div>
                    </div>
                </div>
                <div class="ticket-system-form-actions">
                    <button id="generate-statement-btn" class="ticket-system-btn ticket-system-btn-primary" data-agent-id="${agentId}">عرض كشف الحساب</button>
                    <button id="cancel-statement-btn" class="ticket-system-btn ticket-system-btn-secondary">إلغاء</button>
                </div>
            </div>
            `;
            
            // عرض النموذج
            $("#statement-form").html(formHtml).show();
            
            // ربط الأحداث
            $("#generate-statement-btn").on("click", function() {
                const fromDate = $("#from-date").val();
                const toDate = $("#to-date").val();
                ticket_system.agent.generateStatement(agentId, fromDate, toDate);
            });
            
            $("#cancel-statement-btn").on("click", function() {
                $("#statement-form").html('').hide();
                $("#statement-result").html('').hide();
            });
        },
        
        generateStatement: function(agentId, fromDate, toDate) {
            // عرض مؤشر التحميل
            $("#statement-result").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>جاري توليد كشف الحساب...</p></div>').show();
            
            // الحصول على كشف الحساب
            frappe.call({
                method: "ticket_system.api.get_agent_account_statement",
                args: {
                    agent: agentId,
                    from_date: fromDate || null,
                    to_date: toDate || null
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.agent.renderStatement(response.message);
                    } else {
                        ticket_system.showAlert("لا يمكن الحصول على كشف الحساب", "danger");
                        $("#statement-result").html('').hide();
                    }
                }
            });
        },
        
        renderStatement: function(statement) {
            // عرض كشف الحساب
            let html = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">
                        كشف حساب الوكيل: ${statement.agent.agent_name}
                    </div>
                    <div class="ticket-system-subtitle">
                        الفترة: ${statement.from_date || "البداية"} إلى ${statement.to_date || "النهاية"}
                    </div>
                </div>
                
                <div class="ticket-system-statement-summary">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="statement-item">
                                <div class="statement-label">الرصيد الافتتاحي</div>
                                <div class="statement-value">${statement.opening_balance}</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="statement-item">
                                <div class="statement-label">إجمالي المدين</div>
                                <div class="statement-value">${statement.total_debit}</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="statement-item">
                                <div class="statement-label">إجمالي الدائن</div>
                                <div class="statement-value">${statement.total_credit}</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="statement-item">
                                <div class="statement-label">الرصيد الختامي</div>
                                <div class="statement-value">${statement.closing_balance}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="ticket-system-statement-transactions">
                    <table class="ticket-system-table">
                        <thead>
                            <tr>
                                <th>التاريخ</th>
                                <th>النوع</th>
                                <th>المرجع</th>
                                <th>الوصف</th>
                                <th>مدين</th>
                                <th>دائن</th>
                                <th>العمولة</th>
                                <th>الرصيد</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            // إضافة المعاملات
            if (statement.transactions.length === 0) {
                html += `
                <tr>
                    <td colspan="9" class="text-center">لا توجد معاملات خلال الفترة المحددة</td>
                </tr>
                `;
            } else {
                statement.transactions.forEach(function(transaction) {
                    html += `
                    <tr>
                        <td>${transaction.date}</td>
                        <td>${transaction.type}</td>
                        <td>${transaction.reference}</td>
                        <td>${transaction.description}</td>
                        <td>${transaction.debit}</td>
                        <td>${transaction.credit}</td>
                        <td>${transaction.commission}</td>
                        <td>${transaction.balance}</td>
                        <td>${transaction.status}</td>
                    </tr>
                    `;
                });
            }
            
            html += `
                        </tbody>
                    </table>
                </div>
                
                <div class="ticket-system-statement-actions">
                    <button id="print-statement-btn" class="ticket-system-btn ticket-system-btn-primary">طباعة كشف الحساب</button>
                    <button id="export-statement-btn" class="ticket-system-btn ticket-system-btn-secondary">تصدير إلى Excel</button>
                </div>
            </div>
            `;
            
            $("#statement-result").html(html);
            
            // ربط أحداث الطباعة والتصدير
            $("#print-statement-btn").on("click", function() {
                window.print();
            });
            
            $("#export-statement-btn").on("click", function() {
                ticket_system.agent.exportStatementToExcel(statement);
            });
        },
        
        exportStatementToExcel: function(statement) {
            // تنفيذ تصدير كشف الحساب إلى Excel
            // هذه وظيفة مبسطة، في التطبيق الحقيقي يمكن استخدام مكتبات أكثر تقدماً
            
            let csv = 'التاريخ,النوع,المرجع,الوصف,مدين,دائن,العمولة,الرصيد,الحالة\n';
            
            statement.transactions.forEach(function(transaction) {
                csv += `${transaction.date},${transaction.type},${transaction.reference},"${transaction.description}",${transaction.debit},${transaction.credit},${transaction.commission},${transaction.balance},${transaction.status}\n`;
            });
            
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `كشف_حساب_${statement.agent.agent_code}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },
        
        showPaymentForm: function(agentId) {
            // إنشاء نموذج الدفع
            let formHtml = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">إنشاء دفعة جديدة</div>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="payment-amount">المبلغ</label>
                    <input type="number" class="ticket-system-input" id="payment-amount" min="0" step="0.01" required>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="payment-type">نوع الدفعة</label>
                    <select class="ticket-system-select" id="payment-type" required>
                        <option value="">اختر نوع الدفعة</option>
                        <option value="تسوية">تسوية</option>
                        <option value="دفعة مقدمة">دفعة مقدمة</option>
                        <option value="استرداد">استرداد</option>
                    </select>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="payment-method">طريقة الدفع</label>
                    <select class="ticket-system-select" id="payment-method" required>
                        <option value="">اختر طريقة الدفع</option>
                        <option value="نقداً">نقداً</option>
                        <option value="تحويل بنكي">تحويل بنكي</option>
                        <option value="شيك">شيك</option>
                    </select>
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="payment-reference">المرجع</label>
                    <input type="text" class="ticket-system-input" id="payment-reference">
                </div>
                <div class="ticket-system-form-group">
                    <label class="ticket-system-label" for="payment-notes">ملاحظات</label>
                    <textarea class="ticket-system-input" id="payment-notes" rows="3"></textarea>
                </div>
                <div class="ticket-system-form-actions">
                    <button id="submit-payment-btn" class="ticket-system-btn ticket-system-btn-primary" data-agent-id="${agentId}">إنشاء الدفعة</button>
                    <button id="cancel-payment-btn" class="ticket-system-btn ticket-system-btn-secondary">إلغاء</button>
                </div>
            </div>
            `;
            
            // عرض النموذج
            $("#payment-form").html(formHtml).show();
            
            // ربط الأحداث
            $("#submit-payment-btn").on("click", function() {
                const amount = $("#payment-amount").val();
                const paymentType = $("#payment-type").val();
                const paymentMethod = $("#payment-method").val();
                const reference = $("#payment-reference").val();
                const notes = $("#payment-notes").val();
                
                if (!amount || !paymentType || !paymentMethod) {
                    ticket_system.showAlert("يرجى إدخال جميع البيانات المطلوبة", "warning");
                    return;
                }
                
                ticket_system.agent.createPayment(agentId, amount, paymentType, paymentMethod, reference, notes);
            });
            
            $("#cancel-payment-btn").on("click", function() {
                $("#payment-form").html('').hide();
                $("#payment-result").html('').hide();
            });
        },
        
        createPayment: function(agentId, amount, paymentType, paymentMethod, reference, notes) {
            // عرض مؤشر التحميل
            $("#payment-result").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>جاري إنشاء الدفعة...</p></div>').show();
            
            // إنشاء الدفعة
            frappe.call({
                method: "ticket_system.api.create_agent_payment",
                args: {
                    agent: agentId,
                    amount: amount,
                    payment_type: paymentType,
                    payment_method: paymentMethod,
                    reference: reference || null,
                    notes: notes || null
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.agent.showPaymentConfirmation(response.message);
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء إنشاء الدفعة", "danger");
                        $("#payment-result").html('').hide();
                    }
                }
            });
        },
        
        showPaymentConfirmation: function(payment) {
            // عرض تأكيد الدفعة
            let html = `
            <div class="ticket-system-alert ticket-system-alert-success">
                <h4>تم إنشاء الدفعة بنجاح!</h4>
                <p>رقم الدفعة: ${payment.payment_number}</p>
                <p>المبلغ: ${payment.amount}</p>
                <p>نوع الدفعة: ${payment.payment_type}</p>
                <p>طريقة الدفع: ${payment.payment_method}</p>
                <p>تاريخ الدفع: ${payment.payment_date}</p>
            </div>
            `;
            
            // إضافة روابط للإجراءات
            html += `
            <div class="payment-actions">
                <button id="print-payment-btn" class="ticket-system-btn ticket-system-btn-primary" data-payment-id="${payment.name}">طباعة إيصال الدفع</button>
                <button id="view-agent-btn" class="ticket-system-btn ticket-system-btn-secondary" data-agent-id="${payment.agent}">عرض تفاصيل الوكيل</button>
            </div>
            `;
            
            $("#payment-form").hide();
            $("#payment-result").html(html);
            
            // ربط الأحداث
            $("#print-payment-btn").on("click", function() {
                const paymentId = $(this).data("payment-id");
                ticket_system.agent.printPaymentReceipt(paymentId);
            });
            
            $("#view-agent-btn").on("click", function() {
                const agentId = $(this).data("agent-id");
                $("#payment-form").html('').hide();
                $("#payment-result").html('').hide();
                ticket_system.agent.getAgentDetails(agentId);
            });
        },
        
        printPaymentReceipt: function(paymentId) {
            // طباعة إيصال الدفع
            frappe.call({
                method: "ticket_system.api.print_agent_payment",
                args: {
                    payment: paymentId
                },
                callback: function(response) {
                    if (response.message) {
                        const pdfPath = response.message;
                        window.open(`/files/${pdfPath}`, '_blank');
                    } else {
                        ticket_system.showAlert("حدث خطأ أثناء طباعة إيصال الدفع", "danger");
                    }
                }
            });
        }
    },
    
    // وحدة لوحة التحكم
    dashboard: {
        init: function() {
            this.loadDashboardData();
            this.bindEvents();
        },
        
        bindEvents: function() {
            // حدث تغيير الفترة
            $("#period-selector").on("change", function() {
                ticket_system.dashboard.loadDashboardData($(this).val());
            });
        },
        
        loadDashboardData: function(period = "today") {
            // عرض مؤشر التحميل
            $(".dashboard-widget").html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-2x"></i><p>جاري التحميل...</p></div>');
            
            // الحصول على بيانات لوحة التحكم
            frappe.call({
                method: "ticket_system.api.get_dashboard_data",
                args: {
                    period: period
                },
                callback: function(response) {
                    if (response.message) {
                        ticket_system.dashboard.renderDashboard(response.message);
                    } else {
                        ticket_system.showAlert("لا يمكن الحصول على بيانات لوحة التحكم", "danger");
                    }
                }
            });
        },
        
        renderDashboard: function(data) {
            // عرض إحصائيات المبيعات
            $("#sales-stats").html(`
            <div class="row">
                <div class="col-md-3">
                    <div class="dashboard-stat-card">
                        <div class="stat-icon"><i class="fa fa-ticket"></i></div>
                        <div class="stat-value">${data.total_tickets}</div>
                        <div class="stat-label">التذاكر المباعة</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="dashboard-stat-card">
                        <div class="stat-icon"><i class="fa fa-money"></i></div>
                        <div class="stat-value">${data.total_sales}</div>
                        <div class="stat-label">إجمالي المبيعات</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="dashboard-stat-card">
                        <div class="stat-icon"><i class="fa fa-users"></i></div>
                        <div class="stat-value">${data.total_passengers}</div>
                        <div class="stat-label">عدد الركاب</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="dashboard-stat-card">
                        <div class="stat-icon"><i class="fa fa-bus"></i></div>
                        <div class="stat-value">${data.total_trips}</div>
                        <div class="stat-label">عدد الرحلات</div>
                    </div>
                </div>
            </div>
            `);
            
            // عرض الرحلات القادمة
            let upcomingTripsHtml = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">الرحلات القادمة</div>
                </div>
                <table class="ticket-system-table">
                    <thead>
                        <tr>
                            <th>رقم الرحلة</th>
                            <th>المسار</th>
                            <th>التاريخ</th>
                            <th>وقت المغادرة</th>
                            <th>المقاعد المتاحة</th>
                            <th>الحالة</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            if (data.upcoming_trips.length === 0) {
                upcomingTripsHtml += `
                <tr>
                    <td colspan="6" class="text-center">لا توجد رحلات قادمة</td>
                </tr>
                `;
            } else {
                data.upcoming_trips.forEach(function(trip) {
                    upcomingTripsHtml += `
                    <tr>
                        <td>${trip.trip_code}</td>
                        <td>${trip.route_name}</td>
                        <td>${trip.trip_date}</td>
                        <td>${trip.departure_time}</td>
                        <td>${trip.available_seats} / ${trip.total_seats}</td>
                        <td>${trip.status}</td>
                    </tr>
                    `;
                });
            }
            
            upcomingTripsHtml += `
                    </tbody>
                </table>
            </div>
            `;
            
            $("#upcoming-trips").html(upcomingTripsHtml);
            
            // عرض أحدث الحجوزات
            let recentBookingsHtml = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">أحدث الحجوزات</div>
                </div>
                <table class="ticket-system-table">
                    <thead>
                        <tr>
                            <th>رقم الحجز</th>
                            <th>العميل</th>
                            <th>الرحلة</th>
                            <th>تاريخ الحجز</th>
                            <th>المبلغ</th>
                            <th>الحالة</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            if (data.recent_bookings.length === 0) {
                recentBookingsHtml += `
                <tr>
                    <td colspan="6" class="text-center">لا توجد حجوزات حديثة</td>
                </tr>
                `;
            } else {
                data.recent_bookings.forEach(function(booking) {
                    recentBookingsHtml += `
                    <tr>
                        <td>${booking.booking_number}</td>
                        <td>${booking.customer_name}</td>
                        <td>${booking.trip_code}</td>
                        <td>${booking.booking_date}</td>
                        <td>${booking.total_amount}</td>
                        <td>${booking.booking_status}</td>
                    </tr>
                    `;
                });
            }
            
            recentBookingsHtml += `
                    </tbody>
                </table>
            </div>
            `;
            
            $("#recent-bookings").html(recentBookingsHtml);
            
            // عرض أداء الوكلاء
            let agentPerformanceHtml = `
            <div class="ticket-system-card">
                <div class="ticket-system-header">
                    <div class="ticket-system-title">أداء الوكلاء</div>
                </div>
                <table class="ticket-system-table">
                    <thead>
                        <tr>
                            <th>الوكيل</th>
                            <th>عدد الحجوزات</th>
                            <th>عدد التذاكر</th>
                            <th>إجمالي المبيعات</th>
                            <th>إجمالي العمولات</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            if (data.agent_performance.length === 0) {
                agentPerformanceHtml += `
                <tr>
                    <td colspan="5" class="text-center">لا توجد بيانات أداء للوكلاء</td>
                </tr>
                `;
            } else {
                data.agent_performance.forEach(function(agent) {
                    agentPerformanceHtml += `
                    <tr>
                        <td>${agent.agent_name}</td>
                        <td>${agent.total_bookings}</td>
                        <td>${agent.total_tickets}</td>
                        <td>${agent.total_sales}</td>
                        <td>${agent.total_commission}</td>
                    </tr>
                    `;
                });
            }
            
            agentPerformanceHtml += `
                    </tbody>
                </table>
            </div>
            `;
            
            $("#agent-performance").html(agentPerformanceHtml);
            
            // عرض الرسوم البيانية
            this.renderCharts(data);
        },
        
        renderCharts: function(data) {
            // رسم بياني للمبيعات حسب اليوم
            const salesCtx = document.getElementById('sales-chart').getContext('2d');
            new Chart(salesCtx, {
                type: 'line',
                data: {
                    labels: data.sales_chart.labels,
                    datasets: [{
                        label: 'المبيعات',
                        data: data.sales_chart.values,
                        backgroundColor: 'rgba(26, 115, 232, 0.2)',
                        borderColor: 'rgba(26, 115, 232, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            // رسم بياني للمسارات الأكثر طلباً
            const routesCtx = document.getElementById('routes-chart').getContext('2d');
            new Chart(routesCtx, {
                type: 'bar',
                data: {
                    labels: data.top_routes.labels,
                    datasets: [{
                        label: 'عدد التذاكر',
                        data: data.top_routes.values,
                        backgroundColor: 'rgba(52, 168, 83, 0.2)',
                        borderColor: 'rgba(52, 168, 83, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    },
    
    // عرض تنبيه للمستخدم
    showAlert: function(message, type) {
        const alertClass = `ticket-system-alert ticket-system-alert-${type}`;
        const alertHtml = `<div class="${alertClass}">${message}</div>`;
        
        $("#alert-container").html(alertHtml);
        
        // إخفاء التنبيه بعد 5 ثوانٍ
        setTimeout(function() {
            $("#alert-container").html('');
        }, 5000);
    }
};

// تهيئة النظام عند تحميل الصفحة
$(document).ready(function() {
    ticket_system.init();
});
