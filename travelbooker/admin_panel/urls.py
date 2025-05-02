from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Operators
    path('operators/', views.operators, name='operators'),
    path('operators/add/', views.add_operator, name='add_operator'),
    path('operators/<int:operator_id>/edit/', views.edit_operator, name='edit_operator'),
    path('operators/<int:operator_id>/delete/', views.delete_operator, name='delete_operator'),
    
    # Buses
    path('buses/', views.buses, name='buses'),
    path('buses/add/', views.add_bus, name='add_bus'),
    path('buses/<int:bus_id>/edit/', views.edit_bus, name='edit_bus'),
    path('buses/<int:bus_id>/delete/', views.delete_bus, name='delete_bus'),
    
    # Routes
    path('routes/', views.routes, name='routes'),
    path('routes/add/', views.add_route, name='add_route'),
    path('routes/<int:route_id>/edit/', views.edit_route, name='edit_route'),
    path('routes/<int:route_id>/delete/', views.delete_route, name='delete_route'),
    
    # Schedules
    path('schedules/', views.schedules, name='schedules'),
    path('schedules/add/', views.add_schedule, name='add_schedule'),
    path('schedules/<int:schedule_id>/edit/', views.edit_schedule, name='edit_schedule'),
    path('schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    
    # Bookings
    path('bookings/', views.bookings, name='bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/update-status/', views.update_booking_status, name='update_booking_status'),
    
    # Users
    path('users/', views.users, name='users'),
]
