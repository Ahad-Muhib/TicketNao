import uuid
from datetime import datetime, timedelta

def generate_booking_reference():
    """Generate a unique booking reference number"""
    return 'TB' + uuid.uuid4().hex[:8].upper()

def get_seat_availability(schedule):
    """Get available and booked seats for a schedule"""
    total_seats = schedule.bus.total_seats
    booked_seats = schedule.bookings.filter(status__in=['confirmed', 'pending']).count()
    available_seats = total_seats - booked_seats
    
    return {
        'total': total_seats,
        'booked': booked_seats,
        'available': available_seats
    }

def calculate_journey_duration(departure_time, arrival_time):
    """Calculate duration of journey in hours and minutes"""
    duration = arrival_time - departure_time
    total_minutes = duration.total_seconds() / 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    return {
        'hours': hours,
        'minutes': minutes,
        'total_minutes': total_minutes
    }
