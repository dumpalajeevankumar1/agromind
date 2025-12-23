from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # your app urls
    path('accounts/', include('django.contrib.auth.urls')),
     # adds login, logout, password reset
]
