from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from models import (Route, TrainSchedule, TrainOperator, Train, TrainCoach, TrainSeat, 
                   TrainBooking, TrainBookingSeat, TrainCoachFare)
import uuid
import logging

# Create blueprint
train_bp = Blueprint('train', __name__, url_prefix='/train')

@train_bp.route('/')
def index():
    # Get all routes and operators for display on the train home page
    routes = Route.query.all()
    operators = TrainOperator.query.all()
    now = datetime.now()  # Get current datetime for template
    return render_template('train/index.html', routes=routes, operators=operators, now=now)

@train_bp.route('/search', methods=['GET', 'POST'])
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
            return redirect(url_for('train.index'))
        
        # Find routes matching source and destination
        routes = Route.query.filter(
            db.func.lower(Route.source) == db.func.lower(source),
            db.func.lower(Route.destination) == db.func.lower(destination)
        ).all()
        
        if not routes:
            flash(f'No train routes found from {source} to {destination}.', 'warning')
            return redirect(url_for('train.index'))
        
        # Get all route IDs that match
        route_ids = [route.id for route in routes]
        
        # Find all schedules for these routes on the given date
        next_day = datetime(departure_date.year, departure_date.month, departure_date.day, 23, 59, 59)
        schedules = TrainSchedule.query.filter(
            TrainSchedule.route_id.in_(route_ids),
            TrainSchedule.departure_time >= departure_date,
            TrainSchedule.departure_time <= next_day,
            TrainSchedule.status == 'scheduled'
        ).all()
        
        return render_template('train/search.html', 
                            schedules=schedules, 
                            source=source, 
                            destination=destination, 
                            departure_date=departure_date_str)
    
    # If GET request, redirect to train home page
    return redirect(url_for('train.index'))

@train_bp.route('/schedule/<int:schedule_id>')
def schedule_detail(schedule_id):
    schedule = TrainSchedule.query.get_or_404(schedule_id)
    coach_fares = TrainCoachFare.query.filter_by(schedule_id=schedule_id).all()
    return render_template('train/seat_selection.html', schedule=schedule, coach_fares=coach_fares)

@train_bp.route('/api/coaches/<int:schedule_id>')
def get_coaches(schedule_id):
    schedule = TrainSchedule.query.get_or_404(schedule_id)
    train = schedule.train
    
    # Get all coaches for this train
    coaches = TrainCoach.query.filter_by(train_id=train.id).all()
    coach_fares = TrainCoachFare.query.filter_by(schedule_id=schedule_id).all()
    
    # Create a fare lookup dictionary for easier access
    fare_lookup = {cf.coach_type: cf.fare for cf in coach_fares}
    
    # Get data about coaches and their availability
    coach_data = []
    for coach in coaches:
        seats = TrainSeat.query.filter_by(coach_id=coach.id).all()
        
        # Get all bookings for this schedule to determine which seats are booked
        booked_seat_ids = db.session.query(TrainBookingSeat.seat_id).join(
            TrainBooking, TrainBooking.id == TrainBookingSeat.booking_id
        ).filter(
            TrainBooking.schedule_id == schedule_id,
            TrainBooking.status != 'cancelled'
        ).all()
        
        booked_seat_ids = [seat_id for (seat_id,) in booked_seat_ids]
        
        # Count available seats
        available_seats = len([s for s in seats if s.id not in booked_seat_ids])
        total_seats = len(seats)
        
        coach_data.append({
            'id': coach.id,
            'number': coach.coach_number,
            'type': coach.coach_type,
            'available_seats': available_seats,
            'total_seats': total_seats,
            'fare': fare_lookup.get(coach.coach_type, schedule.base_fare)
        })
    
    return jsonify({
        'coaches': coach_data,
        'base_fare': schedule.base_fare
    })

@train_bp.route('/api/seats/<int:coach_id>/<int:schedule_id>')
def get_seats(coach_id, schedule_id):
    coach = TrainCoach.query.get_or_404(coach_id)
    schedule = TrainSchedule.query.get_or_404(schedule_id)
    
    # Get fare for this coach type
    coach_fare = TrainCoachFare.query.filter_by(
        schedule_id=schedule_id, 
        coach_type=coach.coach_type
    ).first()
    
    # Default to base fare if no specific coach fare is found
    fare = coach_fare.fare if coach_fare else schedule.base_fare
    
    # Get all seats for this coach
    seats = TrainSeat.query.filter_by(coach_id=coach_id).all()
    
    # Get all bookings for this schedule to determine which seats are booked
    booked_seat_ids = db.session.query(TrainBookingSeat.seat_id).join(
        TrainBooking, TrainBooking.id == TrainBookingSeat.booking_id
    ).filter(
        TrainBooking.schedule_id == schedule_id,
        TrainBooking.status != 'cancelled'
    ).all()
    
    booked_seat_ids = [seat_id for (seat_id,) in booked_seat_ids]
    
    # Create a list of seat data for the frontend
    seat_data = []
    for seat in seats:
        seat_data.append({
            'id': seat.id,
            'number': seat.seat_number,
            'berth_type': seat.berth_type,
            'booked': seat.id in booked_seat_ids
        })
    
    return jsonify({
        'seats': seat_data,
        'fare': fare,
        'coach_type': coach.coach_type
    })

@train_bp.route('/book/<int:schedule_id>', methods=['POST'])
@login_required
def book_seats(schedule_id):
    schedule = TrainSchedule.query.get_or_404(schedule_id)
    
    # Get selected seats from form data
    selected_seat_ids = request.form.getlist('seats[]')
    
    if not selected_seat_ids:
        flash('Please select at least one seat.', 'danger')
        return redirect(url_for('train.schedule_detail', schedule_id=schedule_id))
    
    # Get main passenger info
    passenger_name = request.form.get('passenger_name')
    passenger_email = request.form.get('passenger_email')
    passenger_phone = request.form.get('passenger_phone')
    
    if not all([passenger_name, passenger_email, passenger_phone]):
        flash('Please fill in all passenger details.', 'danger')
        return redirect(url_for('train.schedule_detail', schedule_id=schedule_id))
    
    # Check if seats are still available
    selected_seats = TrainSeat.query.filter(TrainSeat.id.in_(selected_seat_ids)).all()
    
    booked_seat_ids = db.session.query(TrainBookingSeat.seat_id).join(
        TrainBooking, TrainBooking.id == TrainBookingSeat.booking_id
    ).filter(
        TrainBooking.schedule_id == schedule_id,
        TrainBooking.status != 'cancelled',
        TrainBookingSeat.seat_id.in_(selected_seat_ids)
    ).all()
    
    booked_seat_ids = [seat_id for (seat_id,) in booked_seat_ids]
    
    if booked_seat_ids:
        flash('Some of the selected seats are no longer available. Please try again.', 'danger')
        return redirect(url_for('train.schedule_detail', schedule_id=schedule_id))
    
    # Create booking reference
    booking_reference = 'T' + str(uuid.uuid4())[:7].upper()
    
    # Calculate total amount
    total_amount = 0
    for i, seat in enumerate(selected_seats):
        coach = seat.coach
        coach_fare = TrainCoachFare.query.filter_by(
            schedule_id=schedule_id, 
            coach_type=coach.coach_type
        ).first()
        seat_fare = coach_fare.fare if coach_fare else schedule.base_fare
        total_amount += seat_fare
    
    # Create booking
    booking = TrainBooking(
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
    
    # Create booking seats with passenger information
    for i, seat in enumerate(selected_seats):
        seat_passenger_name = request.form.get(f'passenger_name_{i}', passenger_name)
        seat_passenger_age = request.form.get(f'passenger_age_{i}', '')
        seat_passenger_gender = request.form.get(f'passenger_gender_{i}', '')
        
        if not seat_passenger_name or not seat_passenger_age or not seat_passenger_gender:
            db.session.rollback()
            flash('Please provide details for all passengers.', 'danger')
            return redirect(url_for('train.schedule_detail', schedule_id=schedule_id))
        
        # Get fare for this seat's coach
        coach = seat.coach
        coach_fare = TrainCoachFare.query.filter_by(
            schedule_id=schedule_id, 
            coach_type=coach.coach_type
        ).first()
        seat_fare = coach_fare.fare if coach_fare else schedule.base_fare
        
        booking_seat = TrainBookingSeat(
            booking_id=booking.id,
            seat_id=seat.id,
            price=seat_fare,
            passenger_name=seat_passenger_name,
            passenger_age=int(seat_passenger_age),
            passenger_gender=seat_passenger_gender
        )
        db.session.add(booking_seat)
    
    try:
        db.session.commit()
        flash('Train booking successful! Your booking reference is ' + booking_reference, 'success')
        return redirect(url_for('train.booking_confirmation', booking_id=booking.id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Train booking error: {str(e)}")
        flash('An error occurred during booking. Please try again.', 'danger')
        return redirect(url_for('train.schedule_detail', schedule_id=schedule_id))

@train_bp.route('/booking/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = TrainBooking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    now = datetime.now()  # Get current datetime for template comparison
    return render_template('train/booking_confirmation.html', booking=booking, now=now)

@train_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = TrainBooking.query.filter_by(user_id=current_user.id).order_by(TrainBooking.booking_date.desc()).all()
    now = datetime.now()  # Get current datetime for template comparison
    return render_template('train/my_bookings.html', bookings=bookings, now=now)

@train_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = TrainBooking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Only allow cancellation if the booking isn't already cancelled
    if booking.status == 'cancelled':
        flash('This booking is already cancelled.', 'warning')
        return redirect(url_for('train.my_bookings'))
    
    booking.status = 'cancelled'
    
    try:
        db.session.commit()
        flash('Train booking cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Train cancellation error: {str(e)}")
        flash('An error occurred while cancelling the booking.', 'danger')
    
    return redirect(url_for('train.my_bookings'))

@train_bp.route('/modify-booking/<int:booking_id>')
@login_required
def modify_booking(booking_id):
    booking = TrainBooking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Check if the booking is eligible for modification
    if booking.status == 'cancelled':
        flash('Cancelled bookings cannot be modified.', 'warning')
        return redirect(url_for('train.my_bookings'))
    
    # Get alternative schedules for the same route
    current_route_id = booking.schedule.route_id
    current_schedule_id = booking.schedule_id
    
    # Get datetime 6 hours from now to enforce modification policy
    six_hours_from_now = datetime.now() + timedelta(hours=6)
    
    # Find alternative schedules
    alternative_schedules = TrainSchedule.query.filter(
        TrainSchedule.route_id == current_route_id,
        TrainSchedule.id != current_schedule_id,
        TrainSchedule.departure_time > six_hours_from_now,  # Must be at least 6 hours in the future
        TrainSchedule.status == 'scheduled'
    ).order_by(TrainSchedule.departure_time).all()
    
    return render_template('train/modify_booking.html', booking=booking, alternative_schedules=alternative_schedules)

@train_bp.route('/update-booking/<int:booking_id>', methods=['POST'])
@login_required
def update_booking(booking_id):
    booking = TrainBooking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Check if the booking is eligible for modification
    if booking.status == 'cancelled':
        flash('Cancelled bookings cannot be modified.', 'warning')
        return redirect(url_for('train.my_bookings'))
    
    # Get the new schedule ID from the form
    new_schedule_id = request.form.get('schedule_id')
    
    if not new_schedule_id:
        flash('Please select a new schedule.', 'danger')
        return redirect(url_for('train.modify_booking', booking_id=booking_id))
    
    # Get the new schedule
    new_schedule = TrainSchedule.query.get_or_404(new_schedule_id)
    
    # Store important booking information before updating
    original_reference = booking.booking_reference
    passenger_name = booking.passenger_name
    passenger_email = booking.passenger_email
    passenger_phone = booking.passenger_phone
    
    # Create a new booking with the same details but for the new schedule
    new_booking = TrainBooking(
        booking_reference=original_reference + '-M',  # Add modifier to indicate modified booking
        user_id=current_user.id,
        schedule_id=new_schedule_id,
        status='confirmed',
        passenger_name=passenger_name,
        passenger_email=passenger_email,
        passenger_phone=passenger_phone,
        total_amount=0  # Will be updated after seat selection
    )
    
    # Mark original booking as cancelled
    booking.status = 'cancelled'
    
    try:
        db.session.add(new_booking)
        db.session.commit()
        
        # Redirect to seat selection for the new booking
        flash('Please select seats for your new train schedule.', 'info')
        return redirect(url_for('train.schedule_detail', schedule_id=new_schedule_id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Train booking modification error: {str(e)}")
        flash('An error occurred while modifying your booking. Please try again.', 'danger')
        return redirect(url_for('train.modify_booking', booking_id=booking_id))