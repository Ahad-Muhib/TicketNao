from django.core.management.base import BaseCommand
from main.models import Route, Bus, Schedule
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create schedule data for the application'

    def handle(self, *args, **kwargs):
        routes = Route.objects.all()
        buses = Bus.objects.all()
        
        if not routes or not buses:
            self.stdout.write(self.style.ERROR('No routes or buses found. Cannot create schedules.'))
            return
            
        # Create schedules
        now = datetime.now()
        count = 0
        
        for route in routes:
            for bus in random.sample(list(buses), k=min(2, buses.count())):
                # Create schedules for next 3 days only (faster)
                for day in range(3):
                    # Create morning and evening departure
                    for hour in [8, 16]:  # 8am and 4pm departures
                        departure_time = now.replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=day)
                        duration_minutes = route.estimated_duration_minutes or 240  # fallback to 4 hours
                        arrival_time = departure_time + timedelta(minutes=duration_minutes)
                        
                        # Calculate fare based on distance and bus type
                        base_fare = float(route.distance_km) * 0.5 if route.distance_km else 500  # 0.5 per km or 500 default
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
                            count += 1
                            if count % 10 == 0:  # Only print every 10th schedule to reduce output
                                self.stdout.write(f'Created schedule {count}: {schedule}')
                        else:
                            self.stdout.write(f'Schedule already exists: {schedule}')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} schedules'))