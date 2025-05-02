from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from models import Route, BusSchedule, BusOperator, Bus, Seat, Booking, BookingSeat
import uuid
import logging

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get all routes for display on the home page
    routes = Route.query.all()
    operators = BusOperator.query.all()
    return render_template('index.html', routes=routes, operators=operators)

@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        departure_date_str = request.form.get('departure_date')
        
        # Parse the date
        try:
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('main.index'))
        
        # Find all routes that match the source and destination
        # Using case-insensitive search to be more flexible with user input
        routes = Route.query.filter(
            db.func.lower(Route.source) == db.func.lower(source),
            db.func.lower(Route.destination) == db.func.lower(destination)
        ).all()
        
        if not routes:
            flash(f'No routes found from {source} to {destination}.', 'warning')
            return redirect(url_for('main.index'))
        
        # Get all route IDs that match
        route_ids = [route.id for route in routes]
        
        # Find all schedules for these routes on the given date
        next_day = datetime(departure_date.year, departure_date.month, departure_date.day, 23, 59, 59)
        schedules = BusSchedule.query.filter(
            BusSchedule.route_id.in_(route_ids),
            BusSchedule.departure_time >= departure_date,
            BusSchedule.departure_time <= next_day,
            BusSchedule.status == 'scheduled'
        ).all()
        
        return render_template('search.html', 
                              schedules=schedules, 
                              source=source, 
                              destination=destination, 
                              departure_date=departure_date_str)
    
    # If GET request, redirect to home page
    return redirect(url_for('main.index'))

@main_bp.route('/schedule/<int:schedule_id>')
def schedule_detail(schedule_id):
    schedule = BusSchedule.query.get_or_404(schedule_id)
    return render_template('seat_selection.html', schedule=schedule)

@main_bp.route('/api/seats/<int:schedule_id>')
def get_seats(schedule_id):
    schedule = BusSchedule.query.get_or_404(schedule_id)
    bus = schedule.bus
    
    # Get all seats for this bus
    seats = Seat.query.filter_by(bus_id=bus.id).all()
    
    # Get all bookings for this schedule to determine which seats are booked
    booked_seat_ids = db.session.query(BookingSeat.seat_id).join(
        Booking, Booking.id == BookingSeat.booking_id
    ).filter(
        Booking.schedule_id == schedule_id,
        Booking.status != 'cancelled'
    ).all()
    
    booked_seat_ids = [seat_id for (seat_id,) in booked_seat_ids]
    
    # Create a list of seat data for the frontend
    seat_data = []
    for seat in seats:
        seat_data.append({
            'id': seat.id,
            'number': seat.seat_number,
            'type': seat.seat_type,
            'booked': seat.id in booked_seat_ids
        })
    
    return jsonify({
        'seats': seat_data,
        'fare': schedule.fare
    })

@main_bp.route('/book/<int:schedule_id>', methods=['POST'])
@login_required
def book_seats(schedule_id):
    schedule = BusSchedule.query.get_or_404(schedule_id)
    
    # Get selected seats from form data
    selected_seat_ids = request.form.getlist('seats[]')
    
    if not selected_seat_ids:
        flash('Please select at least one seat.', 'danger')
        return redirect(url_for('main.schedule_detail', schedule_id=schedule_id))
    
    # Get passenger info
    passenger_name = request.form.get('passenger_name')
    passenger_email = request.form.get('passenger_email')
    passenger_phone = request.form.get('passenger_phone')
    
    if not all([passenger_name, passenger_email, passenger_phone]):
        flash('Please fill in all passenger details.', 'danger')
        return redirect(url_for('main.schedule_detail', schedule_id=schedule_id))
    
    # Check if seats are still available
    selected_seats = Seat.query.filter(Seat.id.in_(selected_seat_ids)).all()
    
    booked_seat_ids = db.session.query(BookingSeat.seat_id).join(
        Booking, Booking.id == BookingSeat.booking_id
    ).filter(
        Booking.schedule_id == schedule_id,
        Booking.status != 'cancelled',
        BookingSeat.seat_id.in_(selected_seat_ids)
    ).all()
    
    booked_seat_ids = [seat_id for (seat_id,) in booked_seat_ids]
    
    if booked_seat_ids:
        flash('Some of the selected seats are no longer available. Please try again.', 'danger')
        return redirect(url_for('main.schedule_detail', schedule_id=schedule_id))
    
    # Create booking reference
    booking_reference = str(uuid.uuid4())[:8].upper()
    
    # Calculate total amount
    total_amount = schedule.fare * len(selected_seats)
    
    # Create booking
    booking = Booking(
        booking_reference=booking_reference,
        user_id=current_user.id,
        schedule_id=schedule_id,
        total_amount=total_amount,
        status='confirmed',
        passenger_name=passenger_name,
        passenger_email=passenger_email,
        passenger_phone=passenger_phone
    )
    
    db.session.add(booking)
    db.session.flush()  # To get the booking ID
    
    # Create booking seats
    for seat in selected_seats:
        booking_seat = BookingSeat(
            booking_id=booking.id,
            seat_id=seat.id,
            price=schedule.fare
        )
        db.session.add(booking_seat)
    
    try:
        db.session.commit()
        flash('Booking successful! Your booking reference is ' + booking_reference, 'success')
        return redirect(url_for('main.booking_confirmation', booking_id=booking.id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Booking error: {str(e)}")
        flash('An error occurred during booking. Please try again.', 'danger')
        return redirect(url_for('main.schedule_detail', schedule_id=schedule_id))

@main_bp.route('/booking/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    return render_template('booking_confirmation.html', booking=booking)

@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    now = datetime.now()  # Get current datetime for template comparison
    return render_template('my_bookings.html', bookings=bookings, now=now)

@main_bp.route('/modify-booking/<int:booking_id>')
@login_required
def modify_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Check if the booking is eligible for modification
    if booking.status == 'cancelled':
        flash('Cancelled bookings cannot be modified.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    # Get alternative schedules for the same route
    current_route_id = booking.schedule.route_id
    current_schedule_id = booking.schedule_id
    
    # Get datetime 6 hours from now to enforce modification policy
    six_hours_from_now = datetime.now() + timedelta(hours=6)
    
    # Find alternative schedules
    alternative_schedules = BusSchedule.query.filter(
        BusSchedule.route_id == current_route_id,
        BusSchedule.id != current_schedule_id,
        BusSchedule.departure_time > six_hours_from_now,  # Must be at least 6 hours in the future
        BusSchedule.status == 'scheduled'
    ).order_by(BusSchedule.departure_time).all()
    
    return render_template('modify_booking.html', booking=booking, alternative_schedules=alternative_schedules)

@main_bp.route('/update-booking/<int:booking_id>', methods=['POST'])
@login_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Check if the booking is eligible for modification
    if booking.status == 'cancelled':
        flash('Cancelled bookings cannot be modified.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    # Get the new schedule ID from the form
    new_schedule_id = request.form.get('schedule_id')
    
    if not new_schedule_id:
        flash('Please select a new schedule.', 'danger')
        return redirect(url_for('main.modify_booking', booking_id=booking_id))
    
    # Get the new schedule
    new_schedule = BusSchedule.query.get_or_404(new_schedule_id)
    
    # Store important booking information before updating
    original_reference = booking.booking_reference
    passenger_name = booking.passenger_name
    passenger_email = booking.passenger_email
    passenger_phone = booking.passenger_phone
    
    # Create a new booking with the same details but for the new schedule
    new_booking = Booking(
        booking_reference=original_reference + '-M',  # Add modifier to indicate modified booking
        user_id=current_user.id,
        schedule_id=new_schedule_id,
        status='confirmed',
        passenger_name=passenger_name,
        passenger_email=passenger_email,
        passenger_phone=passenger_phone,
        total_amount=0  # Will be updated after seat selection
    )
    
    # Mark original booking as cancelled with a note
    booking.status = 'cancelled'
    
    try:
        db.session.add(new_booking)
        db.session.commit()
        
        # Redirect to seat selection for the new booking
        flash('Please select seats for your new schedule.', 'info')
        return redirect(url_for('main.schedule_detail', schedule_id=new_schedule_id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Booking modification error: {str(e)}")
        flash('An error occurred while modifying your booking. Please try again.', 'danger')
        return redirect(url_for('main.modify_booking', booking_id=booking_id))

@main_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Only allow cancellation if the booking isn't already cancelled
    if booking.status == 'cancelled':
        flash('This booking is already cancelled.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    booking.status = 'cancelled'
    
    try:
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Cancellation error: {str(e)}")
        flash('An error occurred while cancelling the booking.', 'danger')
    
    return redirect(url_for('main.my_bookings'))
