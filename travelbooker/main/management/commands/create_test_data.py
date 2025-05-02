from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Operator, Route, Bus, Schedule, Seat
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create test data for the application'

    def handle(self, *args, **kwargs):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write('Superuser already exists')

        # Create operators
        operators = [
            {
                'name': 'Shohagh Paribahan',
                'description': 'One of the oldest and most reliable bus operators in Bangladesh.',
                'contact_email': 'info@shohaghparibahan.com',
                'contact_phone': '+880 1712-123456',
                'logo': 'https://picsum.photos/200'
            },
            {
                'name': 'Green Line',
                'description': 'Premium bus service with AC and luxury options.',
                'contact_email': 'info@greenline.com',
                'contact_phone': '+880 1812-345678',
                'logo': 'https://picsum.photos/200'
            },
            {
                'name': 'Hanif Enterprise',
                'description': 'Largest network of bus routes across Bangladesh.',
                'contact_email': 'info@hanifenterprise.com',
                'contact_phone': '+880 1912-456789',
                'logo': 'https://picsum.photos/200'
            }
        ]

        created_operators = []
        for op_data in operators:
            operator, created = Operator.objects.get_or_create(
                name=op_data['name'],
                defaults=op_data
            )
            created_operators.append(operator)
            if created:
                self.stdout.write(f'Created operator: {operator.name}')
            else:
                self.stdout.write(f'Operator already exists: {operator.name}')

        # Create routes
        routes = [
            {'source': 'Dhaka', 'destination': 'Chittagong', 'distance_km': 250.5, 'estimated_duration_minutes': 360},
            {'source': 'Dhaka', 'destination': 'Cox\'s Bazar', 'distance_km': 390.0, 'estimated_duration_minutes': 540},
            {'source': 'Dhaka', 'destination': 'Sylhet', 'distance_km': 230.0, 'estimated_duration_minutes': 300},
            {'source': 'Chittagong', 'destination': 'Cox\'s Bazar', 'distance_km': 150.0, 'estimated_duration_minutes': 180},
            {'source': 'Dhaka', 'destination': 'Rajshahi', 'distance_km': 260.0, 'estimated_duration_minutes': 360},
            {'source': 'Dhaka', 'destination': 'Khulna', 'distance_km': 280.0, 'estimated_duration_minutes': 390},
        ]

        created_routes = []
        for route_data in routes:
            route, created = Route.objects.get_or_create(
                source=route_data['source'],
                destination=route_data['destination'],
                defaults=route_data
            )
            created_routes.append(route)
            if created:
                self.stdout.write(f'Created route: {route}')
            else:
                self.stdout.write(f'Route already exists: {route}')

        # Create buses
        bus_types = ['AC', 'Non-AC', 'Sleeper', 'Semi-Sleeper', 'Luxury']
        buses_data = []
        for i, operator in enumerate(created_operators):
            for j in range(3):  # 3 buses per operator
                bus_type = random.choice(bus_types)
                bus_data = {
                    'operator': operator,
                    'name': f'{operator.name} {bus_type} {j+1}',
                    'registration_number': f'REG-{operator.id}-{j+1}',
                    'bus_type': bus_type,
                    'total_seats': 36 if bus_type in ['AC', 'Luxury'] else 40,
                    'amenities': 'WiFi, USB Charging, Refreshments' if bus_type in ['AC', 'Luxury'] else 'Basic'
                }
                buses_data.append(bus_data)

        created_buses = []
        for bus_data in buses_data:
            bus, created = Bus.objects.get_or_create(
                registration_number=bus_data['registration_number'],
                defaults=bus_data
            )
            created_buses.append(bus)
            if created:
                self.stdout.write(f'Created bus: {bus.name}')
                # Create seats for the bus
                self.create_seats_for_bus(bus)
            else:
                self.stdout.write(f'Bus already exists: {bus.name}')

        # Create schedules
        now = datetime.now()
        for route in created_routes:
            for bus in random.sample(created_buses, k=min(4, len(created_buses))):
                # Create schedules for next 7 days
                for day in range(7):
                    departure_time = now + timedelta(days=day, hours=random.randint(6, 20))
                    duration_minutes = route.estimated_duration_minutes or 240  # fallback to 4 hours
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)
                    
                    # Calculate fare based on distance and bus type
                    base_fare = route.distance_km * 0.5 if route.distance_km else 500  # 0.5 per km or 500 default
                    # Luxury buses cost more
                    if bus.bus_type in ['AC', 'Luxury']:
                        base_fare *= 1.5
                    elif bus.bus_type == 'Sleeper':
                        base_fare *= 1.3
                    
                    schedule_data = {
                        'route': route,
                        'bus': bus,
                        'departure_time': departure_time,
                        'arrival_time': arrival_time,
                        'fare': round(base_fare, 2),
                        'is_active': True
                    }
                    
                    schedule, created = Schedule.objects.get_or_create(
                        route=route,
                        bus=bus,
                        departure_time=departure_time,
                        defaults=schedule_data
                    )
                    
                    if created:
                        self.stdout.write(f'Created schedule: {schedule}')
                    else:
                        self.stdout.write(f'Schedule already exists: {schedule}')

        self.stdout.write(self.style.SUCCESS('Test data creation completed successfully'))

    def create_seats_for_bus(self, bus):
        """Create seats for a bus"""
        # Standard bus layout (for simplicity)
        rows = 9 if bus.bus_type in ['AC', 'Luxury'] else 10
        seats_per_row = 4  # 2 seats on each side with an aisle
        
        seat_counter = 1
        for row in range(rows):
            for col in range(seats_per_row):
                seat_type = 'Window' if col in [0, 3] else 'Aisle'
                seat_number = f'{row+1}{["A", "B", "C", "D"][col]}'
                
                Seat.objects.create(
                    bus=bus,
                    seat_number=seat_number,
                    seat_type=seat_type,
                    deck='main',
                    position_x=col,
                    position_y=row,
                    is_active=True
                )