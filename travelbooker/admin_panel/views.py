from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from django.http import JsonResponse
from main.models import Operator, Bus, Route, Schedule, Booking, Seat, BookingSeat
from .forms import OperatorForm, BusForm, RouteForm, ScheduleForm

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with overview"""
    # Get counts
    total_operators = Operator.objects.count()
    total_buses = Bus.objects.count()
    total_routes = Route.objects.count()
    total_schedules = Schedule.objects.count()
    
    # Recent bookings
    recent_bookings = Booking.objects.order_by('-booking_date')[:10]
    
    # Booking statistics
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    
    # Revenue
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'total_operators': total_operators,
        'total_buses': total_buses,
        'total_routes': total_routes,
        'total_schedules': total_schedules,
        'recent_bookings': recent_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def operators(request):
    """List all operators"""
    operators_list = Operator.objects.all()
    
    context = {
        'operators': operators_list,
    }
    return render(request, 'admin/operators.html', context)

@login_required
@user_passes_test(is_admin)
def add_operator(request):
    """Add new operator"""
    if request.method == 'POST':
        form = OperatorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Operator added successfully!')
            return redirect('admin_panel:operators')
    else:
        form = OperatorForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/add_operator.html', context)

@login_required
@user_passes_test(is_admin)
def edit_operator(request, operator_id):
    """Edit operator"""
    operator = get_object_or_404(Operator, pk=operator_id)
    
    if request.method == 'POST':
        form = OperatorForm(request.POST, instance=operator)
        if form.is_valid():
            form.save()
            messages.success(request, 'Operator updated successfully!')
            return redirect('admin_panel:operators')
    else:
        form = OperatorForm(instance=operator)
    
    context = {
        'form': form,
        'operator': operator,
    }
    return render(request, 'admin/edit_operator.html', context)

@login_required
@user_passes_test(is_admin)
def delete_operator(request, operator_id):
    """Delete operator"""
    operator = get_object_or_404(Operator, pk=operator_id)
    
    if request.method == 'POST':
        operator.delete()
        messages.success(request, 'Operator deleted successfully!')
        return redirect('admin_panel:operators')
    
    context = {
        'operator': operator,
    }
    return render(request, 'admin/delete_operator.html', context)

@login_required
@user_passes_test(is_admin)
def buses(request):
    """List all buses"""
    buses_list = Bus.objects.all().select_related('operator')
    
    context = {
        'buses': buses_list,
    }
    return render(request, 'admin/buses.html', context)

@login_required
@user_passes_test(is_admin)
def add_bus(request):
    """Add new bus"""
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            bus = form.save()
            
            # Create seats based on total_seats
            total_seats = bus.total_seats
            rows = (total_seats // 4) + (1 if total_seats % 4 > 0 else 0)
            
            for i in range(total_seats):
                row = i // 4
                col = i % 4
                seat_type = 'Window' if col == 0 or col == 3 else 'Aisle'
                
                Seat.objects.create(
                    bus=bus,
                    seat_number=str(i + 1),
                    seat_type=seat_type,
                    position_x=col,
                    position_y=row,
                    is_active=True
                )
            
            messages.success(request, 'Bus added successfully with seats!')
            return redirect('admin_panel:buses')
    else:
        form = BusForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/add_bus.html', context)

@login_required
@user_passes_test(is_admin)
def edit_bus(request, bus_id):
    """Edit bus"""
    bus = get_object_or_404(Bus, pk=bus_id)
    
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('admin_panel:buses')
    else:
        form = BusForm(instance=bus)
    
    context = {
        'form': form,
        'bus': bus,
    }
    return render(request, 'admin/edit_bus.html', context)

@login_required
@user_passes_test(is_admin)
def delete_bus(request, bus_id):
    """Delete bus"""
    bus = get_object_or_404(Bus, pk=bus_id)
    
    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Bus deleted successfully!')
        return redirect('admin_panel:buses')
    
    context = {
        'bus': bus,
    }
    return render(request, 'admin/delete_bus.html', context)

@login_required
@user_passes_test(is_admin)
def routes(request):
    """List all routes"""
    routes_list = Route.objects.all()
    
    context = {
        'routes': routes_list,
    }
    return render(request, 'admin/routes.html', context)

@login_required
@user_passes_test(is_admin)
def add_route(request):
    """Add new route"""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route added successfully!')
            return redirect('admin_panel:routes')
    else:
        form = RouteForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/add_route.html', context)

@login_required
@user_passes_test(is_admin)
def edit_route(request, route_id):
    """Edit route"""
    route = get_object_or_404(Route, pk=route_id)
    
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('admin_panel:routes')
    else:
        form = RouteForm(instance=route)
    
    context = {
        'form': form,
        'route': route,
    }
    return render(request, 'admin/edit_route.html', context)

@login_required
@user_passes_test(is_admin)
def delete_route(request, route_id):
    """Delete route"""
    route = get_object_or_404(Route, pk=route_id)
    
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
        return redirect('admin_panel:routes')
    
    context = {
        'route': route,
    }
    return render(request, 'admin/delete_route.html', context)

@login_required
@user_passes_test(is_admin)
def schedules(request):
    """List all schedules"""
    schedules_list = Schedule.objects.all().select_related('route', 'bus', 'bus__operator')
    
    context = {
        'schedules': schedules_list,
    }
    return render(request, 'admin/schedules.html', context)

@login_required
@user_passes_test(is_admin)
def add_schedule(request):
    """Add new schedule"""
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule added successfully!')
            return redirect('admin_panel:schedules')
    else:
        form = ScheduleForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/add_schedule.html', context)

@login_required
@user_passes_test(is_admin)
def edit_schedule(request, schedule_id):
    """Edit schedule"""
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('admin_panel:schedules')
    else:
        form = ScheduleForm(instance=schedule)
    
    context = {
        'form': form,
        'schedule': schedule,
    }
    return render(request, 'admin/edit_schedule.html', context)

@login_required
@user_passes_test(is_admin)
def delete_schedule(request, schedule_id):
    """Delete schedule"""
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('admin_panel:schedules')
    
    context = {
        'schedule': schedule,
    }
    return render(request, 'admin/delete_schedule.html', context)

@login_required
@user_passes_test(is_admin)
def bookings(request):
    """List all bookings"""
    bookings_list = Booking.objects.all().select_related('user', 'schedule', 'schedule__route', 'schedule__bus').order_by('-booking_date')
    
    context = {
        'bookings': bookings_list,
    }
    return render(request, 'admin/bookings.html', context)

@login_required
@user_passes_test(is_admin)
def booking_detail(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'admin/booking_detail.html', context)

@login_required
@user_passes_test(is_admin)
def update_booking_status(request, booking_id):
    """Update booking status (confirm or cancel)"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['confirmed', 'cancelled']:
            booking.status = status
            booking.save()
            messages.success(request, f'Booking {booking.booking_reference} has been {status}.')
        else:
            messages.error(request, 'Invalid status provided.')
    
    return redirect('admin_panel:booking_detail', booking_id=booking.id)

@login_required
@user_passes_test(is_admin)
def users(request):
    """List all users"""
    from django.contrib.auth.models import User
    users_list = User.objects.all().annotate(booking_count=Count('bookings'))
    
    context = {
        'users': users_list,
    }
    return render(request, 'admin/users.html', context)
