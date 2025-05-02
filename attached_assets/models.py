from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    train_bookings = db.relationship('TrainBooking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Bus related models
class BusOperator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(255))  # URL to logo
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    buses = db.relationship('Bus', backref='operator', lazy=True)

    def __repr__(self):
        return f'<BusOperator {self.name}>'

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    distance_km = db.Column(db.Float)
    estimated_duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bus_schedules = db.relationship('BusSchedule', backref='route', lazy=True)
    train_schedules = db.relationship('TrainSchedule', backref='route', lazy=True)

    def __repr__(self):
        return f'<Route {self.source} to {self.destination}>'

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    bus_type = db.Column(db.String(50))  # AC, Non-AC, Sleeper, etc.
    amenities = db.Column(db.Text)  # Comma separated values or JSON string
    operator_id = db.Column(db.Integer, db.ForeignKey('bus_operator.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seats = db.relationship('Seat', backref='bus', lazy=True)
    schedules = db.relationship('BusSchedule', backref='bus', lazy=True)

    def __repr__(self):
        return f'<Bus {self.name} ({self.registration_number})>'

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_type = db.Column(db.String(20))  # Window, Aisle, Middle, etc.
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('BookingSeat', backref='seat', lazy=True)

    __table_args__ = (db.UniqueConstraint('seat_number', 'bus_id', name='unique_seat_per_bus'),)

    def __repr__(self):
        return f'<Seat {self.seat_number} on Bus {self.bus_id}>'

class BusSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    fare = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in-progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='schedule', lazy=True)

    def __repr__(self):
        return f'<BusSchedule {self.id} - {self.departure_time} to {self.arrival_time}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('bus_schedule.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_email = db.Column(db.String(120), nullable=False)
    passenger_phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seats = db.relationship('BookingSeat', backref='booking', lazy=True)

    def __repr__(self):
        return f'<Booking {self.booking_reference}>'

class BookingSeat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('booking_id', 'seat_id', name='unique_seat_per_booking'),)

    def __repr__(self):
        return f'<BookingSeat for Booking {self.booking_id}, Seat {self.seat_id}>'

# Train related models
class TrainOperator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(255))  # URL to logo
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trains = db.relationship('Train', backref='operator', lazy=True)

    def __repr__(self):
        return f'<TrainOperator {self.name}>'

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    train_number = db.Column(db.String(20), unique=True, nullable=False)
    train_type = db.Column(db.String(50))  # Express, Passenger, Shatabdi, etc.
    amenities = db.Column(db.Text)  # Comma separated values or JSON string
    operator_id = db.Column(db.Integer, db.ForeignKey('train_operator.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    coaches = db.relationship('TrainCoach', backref='train', lazy=True)
    schedules = db.relationship('TrainSchedule', backref='train', lazy=True)

    def __repr__(self):
        return f'<Train {self.name} ({self.train_number})>'

class TrainCoach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_number = db.Column(db.String(10), nullable=False)
    coach_type = db.Column(db.String(20), nullable=False)  # AC1, AC2, AC3, Sleeper, General, etc.
    total_seats = db.Column(db.Integer, nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seats = db.relationship('TrainSeat', backref='coach', lazy=True)

    __table_args__ = (db.UniqueConstraint('coach_number', 'train_id', name='unique_coach_per_train'),)

    def __repr__(self):
        return f'<TrainCoach {self.coach_number} on Train {self.train_id}>'

class TrainSeat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)
    berth_type = db.Column(db.String(20))  # Lower, Middle, Upper, Side Lower, Side Upper, etc.
    coach_id = db.Column(db.Integer, db.ForeignKey('train_coach.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('TrainBookingSeat', backref='seat', lazy=True)

    __table_args__ = (db.UniqueConstraint('seat_number', 'coach_id', name='unique_seat_per_coach'),)

    def __repr__(self):
        return f'<TrainSeat {self.seat_number} in Coach {self.coach_id}>'

class TrainSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    base_fare = db.Column(db.Float, nullable=False)  # Base fare, coach fares will be added
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in-progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('TrainBooking', backref='schedule', lazy=True)
    coach_fares = db.relationship('TrainCoachFare', backref='schedule', lazy=True)

    def __repr__(self):
        return f'<TrainSchedule {self.id} - {self.departure_time} to {self.arrival_time}>'

class TrainCoachFare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('train_schedule.id'), nullable=False)
    coach_type = db.Column(db.String(20), nullable=False)  # AC1, AC2, AC3, Sleeper, General, etc.
    fare = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('schedule_id', 'coach_type', name='unique_coach_fare_per_schedule'),)

    def __repr__(self):
        return f'<TrainCoachFare for {self.coach_type} on Schedule {self.schedule_id}>'

class TrainBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('train_schedule.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_email = db.Column(db.String(120), nullable=False)
    passenger_phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seats = db.relationship('TrainBookingSeat', backref='booking', lazy=True)

    def __repr__(self):
        return f'<TrainBooking {self.booking_reference}>'

class TrainBookingSeat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('train_booking.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('train_seat.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_age = db.Column(db.Integer, nullable=False)
    passenger_gender = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('booking_id', 'seat_id', name='unique_seat_per_train_booking'),)

    def __repr__(self):
        return f'<TrainBookingSeat for Booking {self.booking_id}, Seat {self.seat_id}>'
