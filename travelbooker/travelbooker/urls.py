"""
URL configuration for travelbooker project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('auth/', include('auth_app.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]
