from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Route, Schedule, Booking, BookingSeat, Seat, Operator
import json

def index(request):
    """Homepage with search form"""
    routes = Route.objects.all()
    operators = Operator.objects.filter(is_active=True)
    
    context = {
        'routes': routes,
        'operators': operators,
    }
    return render(request, 'index.html', context)

def search(request):
    """Search for bus schedules"""
    if request.method == 'POST':
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        departure_date_str = request.POST.get('departure_date')
        
        if not source or not destination or not departure_date_str:
            messages.error(request, 'Please fill all required fields.')
            return redirect('main:index')
        
        try:
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
            # Set time to start of day
            departure_date_start = timezone.make_aware(datetime.combine(departure_date, datetime.min.time()))
            # Set time to end of day
            departure_date_end = timezone.make_aware(datetime.combine(departure_date, datetime.max.time()))
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('main:index')
            
        # Get schedules for the route and date
        schedules = Schedule.objects.filter(
            route__source=source,
            route__destination=destination,
            departure_time__gte=departure_date_start,
            departure_time__lte=departure_date_end,
            is_active=True
        ).select_related('route', 'bus', 'bus__operator').order_by('departure_time')
        
        # Get all routes for the search form
        routes = Route.objects.all()
        
        context = {
            'source': source,
            'destination': destination,
            'departure_date': departure_date_str,
            'schedules': schedules,
            'routes': routes,
        }
        return render(request, 'search.html', context)
    
    return redirect('main:index')

def schedule_detail(request, schedule_id):
    """View schedule details and seat selection"""
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    
    context = {
        'schedule': schedule,
    }
    return render(request, 'seat_selection.html', context)

def get_seats(request, schedule_id):
    """API to get seat layout and availability"""
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    
    # Get all seats for the bus
    seats = Seat.objects.filter(bus=schedule.bus, is_active=True)
    
    # Get booked seats for this schedule
    booked_seat_ids = BookingSeat.objects.filter(
        booking__schedule=schedule,
        booking__status__in=['confirmed', 'pending']
    ).values_list('seat_id', flat=True)
    
    # Build seat layout
    seat_data = []
    for seat in seats:
        seat_data.append({
            'id': seat.id,
            'number': seat.seat_number,
            'type': seat.seat_type,
            'deck': seat.deck,
            'x': seat.position_x,
            'y': seat.position_y,
            'booked': seat.id in booked_seat_ids,
        })
    
    data = {
        'seats': seat_data,
        'fare': float(schedule.fare),
        'bus_layout': {
            'rows': max([s.position_y for s in seats]) + 1 if seats else 0,
            'cols': max([s.position_x for s in seats]) + 1 if seats else 0,
            'decks': 1 if not any(s.deck for s in seats) else 2,
        }
    }
    
    return JsonResponse(data)

@login_required
def book_seats(request, schedule_id):
    """Book selected seats"""
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        
        # Get form data
        passenger_name = request.POST.get('passenger_name')
        passenger_email = request.POST.get('passenger_email')
        passenger_phone = request.POST.get('passenger_phone')
        selected_seat_ids = request.POST.get('selected_seat_ids')
        
        if not passenger_name or not passenger_email or not passenger_phone or not selected_seat_ids:
            messages.error(request, 'Please fill all required fields and select at least one seat.')
            return redirect('main:schedule_detail', schedule_id=schedule_id)
        
        # Parse selected seat IDs
        try:
            seat_ids = json.loads(selected_seat_ids)
        except:
            messages.error(request, 'Invalid seat selection.')
            return redirect('main:schedule_detail', schedule_id=schedule_id)
        
        if not seat_ids:
            messages.error(request, 'Please select at least one seat.')
            return redirect('main:schedule_detail', schedule_id=schedule_id)
        
        # Calculate total amount
        total_amount = schedule.fare * len(seat_ids)
        
        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            schedule=schedule,
            passenger_name=passenger_name,
            passenger_email=passenger_email,
            passenger_phone=passenger_phone,
            total_amount=total_amount,
            status='confirmed'
        )
        
        # Add seats to booking
        for seat_id in seat_ids:
            seat = get_object_or_404(Seat, pk=seat_id)
            BookingSeat.objects.create(
                booking=booking,
                seat=seat,
                seat_price=schedule.fare
            )
        
        messages.success(request, 'Booking confirmed successfully!')
        return redirect('main:booking_confirmation', booking_id=booking.id)
    
    return redirect('main:schedule_detail', schedule_id=schedule_id)

@login_required
def booking_confirmation(request, booking_id):
    """Display booking confirmation"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'booking_confirmation.html', context)

@login_required
def my_bookings(request):
    """View all bookings for the user"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    now = timezone.now()
    
    context = {
        'bookings': bookings,
        'now': now,
    }
    return render(request, 'my_bookings.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Check if booking can be cancelled
    if booking.status == 'cancelled':
        messages.error(request, 'This booking is already cancelled.')
    elif booking.schedule.departure_time < timezone.now():
        messages.error(request, 'Cannot cancel a booking for a past journey.')
    else:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f'Booking {booking.booking_reference} has been cancelled successfully.')
    
    return redirect('main:my_bookings')

@login_required
def modify_booking(request, booking_id):
    """Modify a booking"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Check if booking can be modified
    if booking.status == 'cancelled':
        messages.error(request, 'Cannot modify a cancelled booking.')
        return redirect('main:my_bookings')
    elif booking.schedule.departure_time < timezone.now():
        messages.error(request, 'Cannot modify a booking for a past journey.')
        return redirect('main:my_bookings')
    
    # Get alternative schedules for the same route
    alternative_schedules = Schedule.objects.filter(
        route=booking.schedule.route,
        departure_time__gt=timezone.now(),
        is_active=True
    ).exclude(id=booking.schedule.id).order_by('departure_time')
    
    context = {
        'booking': booking,
        'alternative_schedules': alternative_schedules,
    }
    return render(request, 'modify_booking.html', context)

@login_required
def update_booking(request, booking_id):
    """Process booking update"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
        
        # Check if booking can be modified
        if booking.status == 'cancelled':
            messages.error(request, 'Cannot modify a cancelled booking.')
            return redirect('main:my_bookings')
        elif booking.schedule.departure_time < timezone.now():
            messages.error(request, 'Cannot modify a booking for a past journey.')
            return redirect('main:my_bookings')
        
        schedule_id = request.POST.get('schedule_id')
        if not schedule_id:
            messages.error(request, 'Please select a schedule.')
            return redirect('main:modify_booking', booking_id=booking.id)
        
        new_schedule = get_object_or_404(Schedule, pk=schedule_id)
        
        # Update booking with new schedule
        booking.schedule = new_schedule
        booking.save()
        
        # Remove all current seats
        BookingSeat.objects.filter(booking=booking).delete()
        
        messages.success(request, 'Schedule updated. Please select new seats.')
        return redirect('main:schedule_detail', schedule_id=new_schedule.id)
    
    return redirect('main:my_bookings')
