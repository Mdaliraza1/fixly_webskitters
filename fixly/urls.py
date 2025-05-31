from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth', include('registration.urls')),
    path('service',include('service.urls')),
    path('review/',include('review.urls')),
    path('booking/',include('booking.urls'))
]
