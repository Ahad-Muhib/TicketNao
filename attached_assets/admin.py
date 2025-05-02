from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from models import User, BusOperator, Bus, Route, BusSchedule, Seat, Booking, BookingSeat
from datetime import datetime
import logging

# Create blueprint
admin_bp = Blueprint('admin', __name__)

# Admin authentication middleware
@admin_bp.before_request
def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
def dashboard():
    total_users = User.query.count()
    total_buses = Bus.query.count()
    total_routes = Route.query.count()
    total_bookings = Booking.query.count()
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users,
                          total_buses=total_buses,
                          total_routes=total_routes,
                          total_bookings=total_bookings,
                          recent_bookings=recent_bookings)

# Bus Operator Management
@admin_bp.route('/operators')
def operators():
    operators = BusOperator.query.all()
    return render_template('admin/operators.html', operators=operators)

@admin_bp.route('/operators/add', methods=['GET', 'POST'])
def add_operator():
    if request.method == 'POST':
        name = request.form.get('name')
        logo = request.form.get('logo')
        contact_phone = request.form.get('contact_phone')
        contact_email = request.form.get('contact_email')
        description = request.form.get('description')
        
        if not name:
            flash('Operator name is required', 'danger')
            return redirect(url_for('admin.add_operator'))
        
        operator = BusOperator(
            name=name,
            logo=logo,
            contact_phone=contact_phone,
            contact_email=contact_email,
            description=description
        )
        
        try:
            db.session.add(operator)
            db.session.commit()
            flash('Bus operator added successfully', 'success')
            return redirect(url_for('admin.operators'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Add operator error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/add_operator.html')

@admin_bp.route('/operators/<int:operator_id>/edit', methods=['GET', 'POST'])
def edit_operator(operator_id):
    operator = BusOperator.query.get_or_404(operator_id)
    
    if request.method == 'POST':
        operator.name = request.form.get('name')
        operator.logo = request.form.get('logo')
        operator.contact_phone = request.form.get('contact_phone')
        operator.contact_email = request.form.get('contact_email')
        operator.description = request.form.get('description')
        
        try:
            db.session.commit()
            flash('Bus operator updated successfully', 'success')
            return redirect(url_for('admin.operators'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Edit operator error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/edit_operator.html', operator=operator)

@admin_bp.route('/operators/<int:operator_id>/delete', methods=['POST'])
def delete_operator(operator_id):
    operator = BusOperator.query.get_or_404(operator_id)
    
    try:
        db.session.delete(operator)
        db.session.commit()
        flash('Bus operator deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete operator error: {str(e)}")
        flash('Cannot delete operator with associated buses', 'danger')
    
    return redirect(url_for('admin.operators'))

# Bus Management
@admin_bp.route('/buses')
def buses():
    buses = Bus.query.all()
    return render_template('admin/buses.html', buses=buses)

@admin_bp.route('/buses/add', methods=['GET', 'POST'])
def add_bus():
    operators = BusOperator.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        registration_number = request.form.get('registration_number')
        total_seats = request.form.get('total_seats')
        bus_type = request.form.get('bus_type')
        amenities = request.form.get('amenities')
        operator_id = request.form.get('operator_id')
        
        if not all([name, registration_number, total_seats, operator_id]):
            flash('All required fields must be filled', 'danger')
            return render_template('admin/add_bus.html', operators=operators)
        
        try:
            total_seats = int(total_seats)
            if total_seats <= 0:
                raise ValueError("Total seats must be positive")
        except ValueError:
            flash('Total seats must be a positive number', 'danger')
            return render_template('admin/add_bus.html', operators=operators)
        
        # Check if registration number already exists
        if Bus.query.filter_by(registration_number=registration_number).first():
            flash('Registration number already exists', 'danger')
            return render_template('admin/add_bus.html', operators=operators)
        
        bus = Bus(
            name=name,
            registration_number=registration_number,
            total_seats=total_seats,
            bus_type=bus_type,
            amenities=amenities,
            operator_id=operator_id
        )
        
        try:
            db.session.add(bus)
            db.session.flush()  # Get bus ID before committing
            
            # Create seats for this bus
            for i in range(1, total_seats + 1):
                seat_number = str(i)
                seat_type = 'Window' if i % 4 == 0 or i % 4 == 1 else 'Aisle'
                seat = Seat(
                    seat_number=seat_number,
                    seat_type=seat_type,
                    bus_id=bus.id
                )
                db.session.add(seat)
            
            db.session.commit()
            flash('Bus added successfully with ' + str(total_seats) + ' seats', 'success')
            return redirect(url_for('admin.buses'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Add bus error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/add_bus.html', operators=operators)

@admin_bp.route('/buses/<int:bus_id>/edit', methods=['GET', 'POST'])
def edit_bus(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    operators = BusOperator.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        registration_number = request.form.get('registration_number')
        bus_type = request.form.get('bus_type')
        amenities = request.form.get('amenities')
        operator_id = request.form.get('operator_id')
        
        if not all([name, registration_number, operator_id]):
            flash('All required fields must be filled', 'danger')
            return render_template('admin/edit_bus.html', bus=bus, operators=operators)
        
        # Check if registration number already exists and is not this bus
        existing_bus = Bus.query.filter_by(registration_number=registration_number).first()
        if existing_bus and existing_bus.id != bus_id:
            flash('Registration number already exists', 'danger')
            return render_template('admin/edit_bus.html', bus=bus, operators=operators)
        
        bus.name = name
        bus.registration_number = registration_number
        bus.bus_type = bus_type
        bus.amenities = amenities
        bus.operator_id = operator_id
        
        try:
            db.session.commit()
            flash('Bus updated successfully', 'success')
            return redirect(url_for('admin.buses'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Edit bus error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/edit_bus.html', bus=bus, operators=operators)

@admin_bp.route('/buses/<int:bus_id>/delete', methods=['POST'])
def delete_bus(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    
    try:
        # First delete all seats
        Seat.query.filter_by(bus_id=bus_id).delete()
        db.session.delete(bus)
        db.session.commit()
        flash('Bus deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete bus error: {str(e)}")
        flash('Cannot delete bus with associated schedules or bookings', 'danger')
    
    return redirect(url_for('admin.buses'))

# Route Management
@admin_bp.route('/routes')
def routes():
    routes = Route.query.all()
    return render_template('admin/routes.html', routes=routes)

@admin_bp.route('/routes/add', methods=['GET', 'POST'])
def add_route():
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        distance_km = request.form.get('distance_km')
        estimated_duration_minutes = request.form.get('estimated_duration_minutes')
        
        if not all([source, destination]):
            flash('Source and destination are required', 'danger')
            return redirect(url_for('admin.add_route'))
        
        # Check if route already exists
        if Route.query.filter_by(source=source, destination=destination).first():
            flash('Route already exists', 'danger')
            return redirect(url_for('admin.add_route'))
        
        try:
            if distance_km:
                distance_km = float(distance_km)
            if estimated_duration_minutes:
                estimated_duration_minutes = int(estimated_duration_minutes)
        except ValueError:
            flash('Invalid distance or duration', 'danger')
            return redirect(url_for('admin.add_route'))
        
        route = Route(
            source=source,
            destination=destination,
            distance_km=distance_km,
            estimated_duration_minutes=estimated_duration_minutes
        )
        
        try:
            db.session.add(route)
            db.session.commit()
            flash('Route added successfully', 'success')
            return redirect(url_for('admin.routes'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Add route error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/add_route.html')

@admin_bp.route('/routes/<int:route_id>/edit', methods=['GET', 'POST'])
def edit_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        distance_km = request.form.get('distance_km')
        estimated_duration_minutes = request.form.get('estimated_duration_minutes')
        
        if not all([source, destination]):
            flash('Source and destination are required', 'danger')
            return render_template('admin/edit_route.html', route=route)
        
        # Check if route already exists and is not this route
        existing_route = Route.query.filter_by(source=source, destination=destination).first()
        if existing_route and existing_route.id != route_id:
            flash('Route already exists', 'danger')
            return render_template('admin/edit_route.html', route=route)
        
        try:
            if distance_km:
                distance_km = float(distance_km)
            if estimated_duration_minutes:
                estimated_duration_minutes = int(estimated_duration_minutes)
        except ValueError:
            flash('Invalid distance or duration', 'danger')
            return render_template('admin/edit_route.html', route=route)
        
        route.source = source
        route.destination = destination
        route.distance_km = distance_km
        route.estimated_duration_minutes = estimated_duration_minutes
        
        try:
            db.session.commit()
            flash('Route updated successfully', 'success')
            return redirect(url_for('admin.routes'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Edit route error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/edit_route.html', route=route)

@admin_bp.route('/routes/<int:route_id>/delete', methods=['POST'])
def delete_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    try:
        db.session.delete(route)
        db.session.commit()
        flash('Route deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete route error: {str(e)}")
        flash('Cannot delete route with associated schedules', 'danger')
    
    return redirect(url_for('admin.routes'))

# Schedule Management
@admin_bp.route('/schedules')
def schedules():
    schedules = BusSchedule.query.all()
    return render_template('admin/schedules.html', schedules=schedules)

@admin_bp.route('/schedules/add', methods=['GET', 'POST'])
def add_schedule():
    buses = Bus.query.all()
    routes = Route.query.all()
    
    if request.method == 'POST':
        bus_id = request.form.get('bus_id')
        route_id = request.form.get('route_id')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')
        fare = request.form.get('fare')
        status = request.form.get('status', 'scheduled')
        
        if not all([bus_id, route_id, departure_time, arrival_time, fare]):
            flash('All fields are required', 'danger')
            return render_template('admin/add_schedule.html', buses=buses, routes=routes)
        
        try:
            departure_time = datetime.strptime(departure_time, '%Y-%m-%dT%H:%M')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M')
            fare = float(fare)
            
            if departure_time >= arrival_time:
                flash('Departure time must be before arrival time', 'danger')
                return render_template('admin/add_schedule.html', buses=buses, routes=routes)
            
            if fare <= 0:
                flash('Fare must be positive', 'danger')
                return render_template('admin/add_schedule.html', buses=buses, routes=routes)
        except ValueError:
            flash('Invalid date/time format or fare', 'danger')
            return render_template('admin/add_schedule.html', buses=buses, routes=routes)
        
        schedule = BusSchedule(
            bus_id=bus_id,
            route_id=route_id,
            departure_time=departure_time,
            arrival_time=arrival_time,
            fare=fare,
            status=status
        )
        
        try:
            db.session.add(schedule)
            db.session.commit()
            flash('Schedule added successfully', 'success')
            return redirect(url_for('admin.schedules'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Add schedule error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/add_schedule.html', buses=buses, routes=routes)

@admin_bp.route('/schedules/<int:schedule_id>/edit', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    schedule = BusSchedule.query.get_or_404(schedule_id)
    buses = Bus.query.all()
    routes = Route.query.all()
    
    if request.method == 'POST':
        bus_id = request.form.get('bus_id')
        route_id = request.form.get('route_id')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')
        fare = request.form.get('fare')
        status = request.form.get('status')
        
        if not all([bus_id, route_id, departure_time, arrival_time, fare, status]):
            flash('All fields are required', 'danger')
            return render_template('admin/edit_schedule.html', schedule=schedule, buses=buses, routes=routes)
        
        try:
            departure_time = datetime.strptime(departure_time, '%Y-%m-%dT%H:%M')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M')
            fare = float(fare)
            
            if departure_time >= arrival_time:
                flash('Departure time must be before arrival time', 'danger')
                return render_template('admin/edit_schedule.html', schedule=schedule, buses=buses, routes=routes)
            
            if fare <= 0:
                flash('Fare must be positive', 'danger')
                return render_template('admin/edit_schedule.html', schedule=schedule, buses=buses, routes=routes)
        except ValueError:
            flash('Invalid date/time format or fare', 'danger')
            return render_template('admin/edit_schedule.html', schedule=schedule, buses=buses, routes=routes)
        
        schedule.bus_id = bus_id
        schedule.route_id = route_id
        schedule.departure_time = departure_time
        schedule.arrival_time = arrival_time
        schedule.fare = fare
        schedule.status = status
        
        try:
            db.session.commit()
            flash('Schedule updated successfully', 'success')
            return redirect(url_for('admin.schedules'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Edit schedule error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/edit_schedule.html', 
                          schedule=schedule, 
                          buses=buses, 
                          routes=routes,
                          departure_time=schedule.departure_time.strftime('%Y-%m-%dT%H:%M'),
                          arrival_time=schedule.arrival_time.strftime('%Y-%m-%dT%H:%M'))

@admin_bp.route('/schedules/<int:schedule_id>/delete', methods=['POST'])
def delete_schedule(schedule_id):
    schedule = BusSchedule.query.get_or_404(schedule_id)
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete schedule error: {str(e)}")
        flash('Cannot delete schedule with associated bookings', 'danger')
    
    return redirect(url_for('admin.schedules'))

# Booking Management
@admin_bp.route('/bookings')
def bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/bookings/<int:booking_id>')
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('admin/booking_detail.html', booking=booking)

@admin_bp.route('/bookings/<int:booking_id>/update-status', methods=['POST'])
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    status = request.form.get('status')
    
    if status not in ['pending', 'confirmed', 'cancelled']:
        flash('Invalid status', 'danger')
        return redirect(url_for('admin.booking_detail', booking_id=booking_id))
    
    booking.status = status
    
    try:
        db.session.commit()
        flash('Booking status updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Update booking status error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.booking_detail', booking_id=booking_id))

# User Management
@admin_bp.route('/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow removing admin from yourself
    if user.id == current_user.id:
        flash('You cannot change your own admin status', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    
    try:
        db.session.commit()
        flash('User admin status updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Toggle admin error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete user error: {str(e)}")
        flash('Cannot delete user with associated bookings', 'danger')
    
    return redirect(url_for('admin.users'))
