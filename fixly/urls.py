from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registration.urls')),
    path('services/',include('service.urls')),
    path('review/',include('review.urls')),
    path('booking/',include('booking.urls'))
]
