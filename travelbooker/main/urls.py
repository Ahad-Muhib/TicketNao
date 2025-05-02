from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('schedule/<int:schedule_id>/', views.schedule_detail, name='schedule_detail'),
    path('api/schedule/<int:schedule_id>/seats/', views.get_seats, name='get_seats'),
    path('book/<int:schedule_id>/', views.book_seats, name='book_seats'),
    path('booking/<int:booking_id>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/modify/', views.modify_booking, name='modify_booking'),
    path('booking/<int:booking_id>/update/', views.update_booking, name='update_booking'),
]
