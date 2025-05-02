from django.contrib import admin
from .models import Operator, Route, Bus, Schedule, Seat, Booking, BookingSeat

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_email')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'distance_km', 'estimated_duration_minutes')
    search_fields = ('source', 'destination')

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('name', 'operator', 'registration_number', 'bus_type', 'total_seats', 'is_active')
    list_filter = ('bus_type', 'is_active', 'operator')
    search_fields = ('name', 'registration_number', 'operator__name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'bus', 'departure_time', 'arrival_time', 'fare', 'is_active')
    list_filter = ('is_active', 'bus__operator', 'departure_time')
    search_fields = ('route__source', 'route__destination', 'bus__name')
    date_hierarchy = 'departure_time'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('bus', 'seat_number', 'seat_type', 'deck', 'position_x', 'position_y', 'is_active')
    list_filter = ('seat_type', 'deck', 'is_active', 'bus')
    search_fields = ('seat_number', 'bus__name')

class BookingSeatInline(admin.TabularInline):
    model = BookingSeat
    extra = 0
    readonly_fields = ('seat', 'seat_price')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user', 'schedule', 'passenger_name', 'booking_date', 'total_amount', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('booking_reference', 'passenger_name', 'passenger_email')
    date_hierarchy = 'booking_date'
    inlines = [BookingSeatInline]
