from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime

class Operator(models.Model):
    """Bus operator model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    """Route model for bus journeys"""
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    estimated_duration_minutes = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('source', 'destination')

    def __str__(self):
        return f"{self.source} → {self.destination}"

class Bus(models.Model):
    """Bus model"""
    BUS_TYPES = (
        ('AC', 'AC'),
        ('Non-AC', 'Non-AC'),
        ('Sleeper', 'Sleeper'),
        ('Semi-Sleeper', 'Semi-Sleeper'),
        ('Luxury', 'Luxury'),
    )
    
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='buses')
    name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES)
    total_seats = models.IntegerField()
    is_active = models.BooleanField(default=True)
    amenities = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.operator.name})"

class Schedule(models.Model):
    """Bus schedule model"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    fare = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.route} - {self.departure_time.strftime('%d %b %Y, %H:%M')}"

class Seat(models.Model):
    """Seat model for buses"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=20, blank=True, null=True)  # window, aisle, etc.
    deck = models.CharField(max_length=10, blank=True, null=True)  # upper, lower
    position_x = models.IntegerField()  # for seat layout visualization
    position_y = models.IntegerField()  # for seat layout visualization
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('bus', 'seat_number')

    def __str__(self):
        return f"{self.bus.name} - Seat {self.seat_number}"

class Booking(models.Model):
    """Booking model"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='bookings')
    booking_reference = models.CharField(max_length=10, unique=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.passenger_name}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate a unique booking reference
            self.booking_reference = 'TB' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

class BookingSeat(models.Model):
    """Model to represent seat allocation in a booking"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    seat_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('booking', 'seat')

    def __str__(self):
        return f"{self.booking.booking_reference} - Seat {self.seat.seat_number}"
